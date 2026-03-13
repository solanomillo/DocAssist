"""
Motor RAG (Retrieval-Augmented Generation) para DocAssist
Con manejo de cuotas y límites de API - VERSIÓN ACTUALIZADA
"""

import os
import shutil
import tempfile
import time
from typing import List, Optional, Callable
from pathlib import Path
import uuid

# IMPORTACIONES ACTUALIZADAS
from langchain_chroma import Chroma  # Nuevo import en lugar de langchain_community.vectorstores
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Importaciones específicas por proveedor
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from google.api_core.exceptions import ResourceExhausted


# Esto fuerza a PyInstaller a incluir estos módulos
import chromadb
import chromadb.api
import chromadb.api.client
import chromadb.api.models
import chromadb.api.types
import chromadb.db
import chromadb.ingest
import chromadb.telemetry
import chromadb.telemetry.product



class QuotaExceededError(Exception):
    """Excepción personalizada para cuando se excede la cuota"""
    pass


class RAGEngine:
    """
    Clase principal del motor RAG con manejo de cuotas
    Versión actualizada sin warnings de deprecación
    """
    
    CHROMA_TEMP_DIR = Path(tempfile.gettempdir()) / "docassist_chroma"
    
    # Configuración de límites según plan
    FREE_TIER_LIMITS = {
        "batch_size": 50,
        "pause_seconds": 65,
        "max_retries": 3,
        "daily_limit": 1500,
    }
    
    PAID_TIER_LIMITS = {
        "batch_size": 500,
        "pause_seconds": 1,
        "max_retries": 5,
        "daily_limit": 50000,
    }
    
    def __init__(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None, is_paid_plan: bool = False):
        """
        Inicializa el motor RAG
        
        Args:
            provider: Proveedor (OpenAI, Anthropic, Google Gemini, Ollama)
            api_key: API key
            model: Modelo a usar
            is_paid_plan: True si es plan de pago, False si es gratis
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.is_paid_plan = is_paid_plan
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.chat_history = []
        self.cancel_requested = False
        self.progress_callback = None
        
        # Configurar límites según plan
        self.limits = self.PAID_TIER_LIMITS if is_paid_plan else self.FREE_TIER_LIMITS
        
        # Configurar el proveedor
        self._setup_provider()
        plan_tipo = "PAGO" if is_paid_plan else "GRATUITO"
        print(f"✅ RAGEngine inicializado: {self.provider} - {self.model} (Plan {plan_tipo})")
        print(f"📊 Límites: batch_size={self.limits['batch_size']}, pausa={self.limits['pause_seconds']}s")
    
    def cancel_processing(self):
        """Cancela el procesamiento en curso"""
        self.cancel_requested = True
        print("⏹️ Cancelación solicitada por el usuario")
    
    def _setup_provider(self):
        """Configura el proveedor de IA"""
        try:
            if self.provider == "OpenAI":
                self._setup_openai()
            elif self.provider == "Anthropic":
                self._setup_anthropic()
            elif self.provider == "Google Gemini":
                self._setup_gemini()
            elif self.provider == "Ollama":
                self._setup_ollama()
                # Ollama es local, siempre es "gratis" pero sin límites
                self.is_paid_plan = True
                self.limits = self.PAID_TIER_LIMITS
            else:
                raise ValueError(f"Proveedor no soportado: {self.provider}")
        except Exception as e:
            print(f"❌ Error configurando proveedor: {e}")
            raise
    
    def _setup_openai(self):
        if not self.api_key:
            raise ValueError("API key requerida para OpenAI")
        self.llm = ChatOpenAI(api_key=self.api_key, model=self.model, temperature=0.7)
        self.embeddings = OpenAIEmbeddings(api_key=self.api_key)
        print(f"🔧 OpenAI configurado con modelo: {self.model}")
    
    def _setup_anthropic(self):
        if not self.api_key:
            raise ValueError("API key requerida para Anthropic")
        self.llm = ChatAnthropic(api_key=self.api_key, model=self.model, temperature=0.7)
        # Usar OpenAI para embeddings
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Anthropic requiere API key de OpenAI para embeddings")
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        print(f"🔧 Anthropic configurado con modelo: {self.model}")
    
    def _setup_gemini(self):
        if not self.api_key:
            raise ValueError("API key requerida para Google Gemini")
        
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model=self.model,
            temperature=0.7
        )
        print(f"🔧 Google Gemini LLM configurado con modelo: {self.model}")
        
        # Configurar embeddings con manejo de errores
        embedding_models = [
            "models/gemini-embedding-001",
            "models/gemini-embedding-2-preview",
        ]
        
        for emb_model in embedding_models:
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    google_api_key=self.api_key,
                    model=emb_model
                )
                # Verificar que funciona
                test_vec = self.embeddings.embed_query("test")
                if test_vec and len(test_vec) > 0:
                    print(f"✅ Embeddings funcionando con: {emb_model}")
                    return
            except Exception as e:
                print(f"   ⚠️ Error con {emb_model}: {str(e)[:100]}...")
                continue
        
        raise Exception("No se pudo configurar embeddings para Gemini")
    
    def _setup_ollama(self):
        self.llm = Ollama(model=self.model, temperature=0.7)
        self.embeddings = OllamaEmbeddings(model=self.model)
        print(f"🔧 Ollama configurado con modelo local: {self.model}")
    
    def _create_vectorstore_with_rate_limit(self, chunks: List[Document]) -> bool:
        """
        Crea vectorstore respetando límites de tasa para APIs gratuitas
        Versión actualizada sin persist() manual
        """
        print("🔄 Usando modo de procesamiento por lotes con control de tasa")
        
        total_chunks = len(chunks)
        batch_size = self.limits["batch_size"]
        pause_seconds = self.limits["pause_seconds"]
        max_retries = self.limits["max_retries"]
        
        # Crear vectorstore vacío - En Chroma nuevo no necesita persist_directory explícito
        # Los documentos se guardan automáticamente
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=str(self.CHROMA_TEMP_DIR)
        )
        
        for i in range(0, total_chunks, batch_size):
            # Verificar cancelación
            if self.cancel_requested:
                print("⏹️ Procesamiento cancelado por el usuario")
                return False
            
            batch = chunks[i:i+batch_size]
            batch_num = i//batch_size + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size
            
            # Reportar progreso
            if self.progress_callback:
                progress = int((i / total_chunks) * 100)
                self.progress_callback(
                    progress, 
                    f"Lote {batch_num}/{total_batches} - {len(batch)} chunks"
                )
            
            print(f"\n📦 Procesando lote {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            # Intentar procesar el lote con reintentos
            for attempt in range(max_retries):
                try:
                    self.vectorstore.add_documents(batch)
                    print(f"✅ Lote {batch_num} completado")
                    break
                    
                except ResourceExhausted as e:
                    # Error específico de cuota agotada
                    wait_time = pause_seconds * (attempt + 1)
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ Cuota agotada. Reintento {attempt + 1}/{max_retries} en {wait_time}s...")
                        
                        if self.progress_callback:
                            self.progress_callback(
                                int((i / total_chunks) * 100),
                                f"Cuota agotada, esperando {wait_time}s..."
                            )
                        
                        # Pausa con posibilidad de cancelación
                        for s in range(wait_time):
                            if self.cancel_requested:
                                return False
                            time.sleep(1)
                    else:
                        # Agotamos los reintentos
                        error_msg = self._get_quota_error_message(i, total_chunks)
                        raise QuotaExceededError(error_msg)
                        
                except Exception as e:
                    # Otros errores
                    if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                        wait_time = pause_seconds * (attempt + 1)
                        print(f"⚠️ Posible límite de tasa. Esperando {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Error en lote {batch_num}: {e}")
                        raise
            
            # Pausa entre lotes (excepto después del último)
            if i + batch_size < total_chunks and not self.cancel_requested:
                print(f"⏳ Pausa de {pause_seconds} segundos antes del siguiente lote...")
                
                if self.progress_callback:
                    self.progress_callback(
                        int((i / total_chunks) * 100),
                        f"Pausa de {pause_seconds}s para respetar límites..."
                    )
                
                # Pausa con posibilidad de cancelación
                for s in range(pause_seconds):
                    if self.cancel_requested:
                        return False
                    time.sleep(1)
        
        # No necesitamos llamar a persist() - Chroma nuevo guarda automáticamente
        return True
    
    def _get_quota_error_message(self, processed: int, total: int) -> str:
        """Genera mensaje de error de cuota amigable"""
        plan_msg = "GRATUITO" if not self.is_paid_plan else "ACTUAL"
        
        if self.provider == "Google Gemini":
            suggestion = (
                "Para Gemini Free: 100 solicitudes por minuto.\n"
                "• Espera 60-65 segundos y vuelve a intentar\n"
                "• Considera actualizar a un plan de pago\n"
                "• Usa lotes más pequeños o reduce chunks"
            )
        elif self.provider == "OpenAI":
            suggestion = (
                "Para OpenAI Free: límites variables.\n"
                "• Verifica tu saldo en platform.openai.com\n"
                "• Considera agregar método de pago"
            )
        else:
            suggestion = "Espera unos minutos y vuelve a intentar."
        
        return (
            f"\n❌ LÍMITE DE CUOTA ALCANZADO\n"
            f"Proveedor: {self.provider}\n"
            f"Plan: {plan_msg}\n"
            f"Progreso: {processed}/{total} chunks procesados\n\n"
            f"💡 Sugerencias:\n{suggestion}"
        )
    
    def _create_session_folder(self):
        """Crea una carpeta única para esta sesión"""        
        session_id = uuid.uuid4().hex[:8]
        self.CHROMA_TEMP_DIR = Path(tempfile.gettempdir()) / f"docassist_{session_id}"
        print(f"📁 Usando carpeta temporal: {self.CHROMA_TEMP_DIR}")
        return self.CHROMA_TEMP_DIR


    def load_documents(self, file_paths: List[str], progress_callback: Optional[Callable] = None) -> bool:
        """
        Carga documentos en el motor RAG - SIEMPRE EMPIEZA DESDE CERO
        
        Args:
            file_paths: Lista de rutas a documentos
            progress_callback: Función para reportar progreso
                
        Returns:
            bool: True si exitoso
        """
        self.cancel_requested = False
        self.progress_callback = progress_callback
        
        # SIEMPRE limpiar y crear carpeta nueva para empezar desde cero
        print("\n🔄 ===== NUEVA SESIÓN - LIMPIANDO ANTERIOR =====")
        self.clear_vectorstore(force=True)
        self._create_session_folder()  # Carpeta única para esta carga
        
        try:
            print(f"\n📚 Procesando {len(file_paths)} documento(s)...")
            
            if progress_callback:
                progress_callback(5, "Procesando documentos...")
            
            # 1. Procesar documentos (cargar y dividir)
            chunks = self._process_documents(file_paths)
            
            if not chunks:
                print("❌ No se pudieron procesar los documentos")
                return False
            
            print(f"📚 Total: {len(chunks)} chunks generados")
            
            if progress_callback:
                progress_callback(15, f"Generando embeddings ({len(chunks)} chunks)...")
            
            # 2. Crear vectorstore con control de tasa
            success = self._create_vectorstore_with_rate_limit(chunks)
            
            if success:
                if progress_callback:
                    progress_callback(100, "¡Completado!")
                print(f"✅ {len(chunks)} chunks procesados correctamente")
                print(f"📚 ===== CARGA COMPLETADA =====\n")
                return True
            else:
                print("⏹️ Carga cancelada")
                return False
                
        except QuotaExceededError as e:
            print(f"❌ Error de cuota: {e}")
            if progress_callback:
                progress_callback(0, "CUOTA AGOTADA")
            raise
            
        except Exception as e:
            print(f"❌ Error cargando documentos: {e}")
            import traceback
            traceback.print_exc()
            if progress_callback:
                progress_callback(0, f"Error: {str(e)[:50]}...")
            return False
    
    def _process_documents(self, file_paths: List[str]) -> List[Document]:
        """Procesa documentos: carga y divide en chunks"""
        all_documents = []
        
        for file_path in file_paths:
            file_path = str(file_path)
            extension = Path(file_path).suffix.lower()
            
            print(f"📄 Cargando: {Path(file_path).name}")
            
            try:
                if extension == '.pdf':
                    loader = PyPDFLoader(file_path)
                    documents = loader.load()
                    print(f"   📑 {len(documents)} páginas cargadas")
                elif extension == '.txt':
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents = loader.load()
                    print(f"   📝 Documento de texto cargado")
                else:
                    print(f"   ⚠️ Formato no soportado: {extension}")
                    continue
                
                for doc in documents:
                    doc.metadata['source'] = file_path
                    doc.metadata['type'] = extension[1:]
                all_documents.extend(documents)
                
            except Exception as e:
                print(f"   ❌ Error cargando {file_path}: {e}")
        
        if not all_documents:
            return []
        
        print(f"\n📚 Total: {len(all_documents)} páginas/fragmentos cargados")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200,
            length_function=len, separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(all_documents)
        print(f"✂️  Divididos en {len(chunks)} chunks")
        
        return chunks
    
    def ask(self, question: str) -> str:
        """Realiza una pregunta al motor RAG"""
        if self.vectorstore is None:
            return "⚠️ No hay documentos cargados. Por favor, carga algunos documentos primero."
        
        try:
            print(f"\n❓ Pregunta: {question}")
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
            docs = retriever.invoke(question)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            history_text = ""
            if self.chat_history:
                history_text = "\nHistorial de la conversación:\n"
                for q, a in self.chat_history[-3:]:
                    history_text += f"Usuario: {q}\nAsistente: {a}\n"
            
            prompt = f"""Basándote en el siguiente contexto, responde la pregunta del usuario.

            Contexto:
            {context}

            {history_text}
            Pregunta actual: {question}

            Respuesta (basada SOLO en el contexto proporcionado):"""
            
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            self.chat_history.append((question, answer))
            return answer
            
        except ResourceExhausted as e:
            error_msg = "⚠️ Límite de API excedido. Por favor, espera unos minutos y vuelve a intentar."
            print(f"❌ {e}")
            return error_msg
            
        except Exception as e:
            error_msg = f"❌ Error al procesar la pregunta: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_document_count(self) -> int:
        if self.vectorstore:
            try:
                return self.vectorstore._collection.count()
            except:
                return 0
        return 0
    
    def get_document_names(self) -> List[str]:
        if not self.vectorstore:
            return []
        try:
            data = self.vectorstore.get()
            metadatas = data.get('metadatas', [])
            sources = set()
            for meta in metadatas:
                if meta and 'source' in meta:
                    sources.add(os.path.basename(meta['source']))
            return sorted(list(sources))
        except:
            return []
    
    def clear_vectorstore(self, force=False):
        """
        Limpia la base de datos vectorial de manera segura
        
        Args:
            force: Si True, intenta eliminar archivos aunque estén bloqueados
        """
        print("🧹 Limpiando vectorstore...")
        
        # 1. Primero, eliminar la referencia al vectorstore
        if self.vectorstore is not None:
            try:
                # Intentar cerrar la conexión de ChromaDB
                if hasattr(self.vectorstore, '_collection'):
                    self.vectorstore._collection = None
                if hasattr(self.vectorstore, '_client'):
                    self.vectorstore._client = None
            except:
                pass
            self.vectorstore = None
        
        # 2. Limpiar historial
        self.chat_history = []
        
        # 3. Intentar eliminar la carpeta temporal
        if self.CHROMA_TEMP_DIR.exists():
            import time
            import shutil
            
            # Intentar hasta 3 veces con pausas
            for intento in range(3):
                try:
                    shutil.rmtree(self.CHROMA_TEMP_DIR)
                    print(f"✅ Vectorstore eliminado: {self.CHROMA_TEMP_DIR}")
                    return True
                except PermissionError as e:
                    print(f"⚠️ Intento {intento + 1}: Archivos bloqueados, esperando...")
                    time.sleep(1)  # Esperar 1 segundo
                    if intento == 2:  # Último intento
                        if force:
                            # Modo forzado: intentar con comandos del sistema
                            import subprocess
                            try:
                                subprocess.run(
                                    f'rmdir /s /q "{self.CHROMA_TEMP_DIR}"', 
                                    shell=True, 
                                    capture_output=True
                                )
                                print("✅ Eliminado con comando del sistema")
                                return True
                            except:
                                print("❌ No se pudo eliminar la carpeta")
                        else:
                            print("⚠️ No se pudo eliminar, se usará una carpeta nueva")
            return False
        return True
    
    def __del__(self):
        pass