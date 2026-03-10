"""
Motor RAG (Retrieval-Augmented Generation) para DocAssist
Gestiona la interacción con modelos de IA y el procesamiento de documentos
"""

import os
import shutil
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path

# Importaciones de LangChain
from langchain_community.embeddings import OpenAIEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Importaciones locales
from core.document_loader import DocumentLoader


class RAGEngine:
    """
    Clase principal del motor RAG
    Maneja la inicialización de modelos, carga de documentos y consultas
    Versión con ChromaDB y procesamiento real de documentos
    """
    
    # Carpeta temporal para ChromaDB
    CHROMA_TEMP_DIR = Path(tempfile.gettempdir()) / "docassist_chroma"
    
    def __init__(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa el motor RAG según el proveedor seleccionado
        
        Args:
            provider: Nombre del proveedor (OpenAI, Anthropic, Google Gemini, Ollama)
            api_key: API key (puede ser None para Ollama)
            model: Nombre del modelo a utilizar
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        
        # Atributos que se inicializarán después
        self.llm = None  # Modelo de lenguaje
        self.embeddings = None  # Modelo de embeddings
        self.vectorstore = None  # Base de datos vectorial
        self.qa_chain = None  # Cadena de preguntas y respuestas
        self.memory = None  # Memoria conversacional
        
        # Document loader
        self.document_loader = DocumentLoader()
        
        # Configurar el proveedor
        self._setup_provider()
        
        print(f"✅ RAGEngine inicializado: {self.provider} - {self.model}")
    
    def _setup_provider(self):
        """
        Configura el proveedor de IA seleccionado
        """
        try:
            if self.provider == "OpenAI":
                self._setup_openai()
            elif self.provider == "Anthropic":
                self._setup_anthropic()
            elif self.provider == "Google Gemini":
                self._setup_gemini()
            elif self.provider == "Ollama":
                self._setup_ollama()
            else:
                raise ValueError(f"Proveedor no soportado: {self.provider}")
                
        except Exception as e:
            print(f"❌ Error configurando proveedor {self.provider}: {e}")
            raise
    
    def _setup_openai(self):
        """Configura OpenAI"""
        if not self.api_key:
            raise ValueError("API key requerida para OpenAI")
        
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=0.7
        )
        
        self.embeddings = OpenAIEmbeddings(
            api_key=self.api_key
        )
        
        print(f"🔧 OpenAI configurado con modelo: {self.model}")
    
    def _setup_anthropic(self):
        """Configura Anthropic"""
        if not self.api_key:
            raise ValueError("API key requerida para Anthropic")
        
        from langchain_anthropic import ChatAnthropic
        from langchain_community.embeddings import OpenAIEmbeddings  # Temporal
        
        self.llm = ChatAnthropic(
            anthropic_api_key=self.api_key,
            model=self.model,
            temperature=0.7
        )
        
        # Temporal: usar OpenAI para embeddings hasta que Anthropic los tenga
        print("⚠️  Usando OpenAI para embeddings (temporal)")
        self.embeddings = OpenAIEmbeddings(
            api_key=self.api_key
        )
        
        print(f"🔧 Anthropic configurado con modelo: {self.model}")
    
    def _setup_gemini(self):
        """Configura Google Gemini"""
        if not self.api_key:
            raise ValueError("API key requerida para Google Gemini")
        
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model=self.model,
            temperature=0.7
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=self.api_key,
            model="models/embedding-001"
        )
        
        print(f"🔧 Google Gemini configurado con modelo: {self.model}")
    
    def _setup_ollama(self):
        """Configura Ollama (modelos locales)"""
        from langchain_community.llms import Ollama
        from langchain_community.embeddings import OllamaEmbeddings
        
        self.llm = Ollama(
            model=self.model,
            temperature=0.7
        )
        
        self.embeddings = OllamaEmbeddings(
            model=self.model
        )
        
        print(f"🔧 Ollama configurado con modelo local: {self.model}")
        print("   📌 Modelo gratuito - sin API key requerida")
    
    def load_documents(self, file_paths: List[str]) -> bool:
        """
        Carga documentos en el motor RAG
        
        Args:
            file_paths: Lista de rutas a los documentos a cargar
            
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            print(f"\n📚 Procesando {len(file_paths)} documento(s)...")
            
            # 1. Procesar documentos (cargar y dividir en chunks)
            chunks = self.document_loader.process_documents(file_paths)
            
            if not chunks:
                print("❌ No se pudieron procesar los documentos")
                return False
            
            # 2. Crear o actualizar vectorstore
            if self.vectorstore is None:
                # Crear nuevo vectorstore
                print("🆕 Creando nueva base de datos vectorial...")
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=str(self.CHROMA_TEMP_DIR)
                )
            else:
                # Añadir a vectorstore existente
                print("➕ Añadiendo documentos a base existente...")
                self.vectorstore.add_documents(chunks)
            
            # 3. Persistir la base de datos
            self.vectorstore.persist()
            print(f"💾 Base de datos vectorial guardada en: {self.CHROMA_TEMP_DIR}")
            
            # 4. Crear el chain conversacional (si no existe)
            if self.qa_chain is None:
                self._create_qa_chain()
            
            print(f"✅ {len(chunks)} chunks procesados correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando documentos: {e}")
            return False
    
    def _create_qa_chain(self):
        """Crea el chain conversacional con memoria"""
        if self.vectorstore is None:
            print("⚠️ No se puede crear QA chain: vectorstore no inicializado")
            return
        
        # Crear memoria para la conversación
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Crear el retriever
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 4}  # Recuperar top 4 chunks
        )
        
        # Crear el chain conversacional
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,  # Para depuración
            verbose=True  # Muestra el proceso
        )
        
        print("🤖 Chain conversacional creado")
    
    def ask(self, question: str) -> str:
        """
        Realiza una pregunta al motor RAG
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            str: Respuesta basada en los documentos
        """
        # Verificar que hay documentos cargados
        if self.vectorstore is None:
            return "⚠️ No hay documentos cargados. Por favor, carga algunos documentos primero."
        
        # Verificar que el chain está creado
        if self.qa_chain is None:
            self._create_qa_chain()
            if self.qa_chain is None:
                return "❌ Error: No se pudo crear el sistema de preguntas y respuestas."
        
        try:
            print(f"\n❓ Pregunta: {question}")
            
            # Ejecutar la consulta
            result = self.qa_chain.invoke({"question": question})
            
            # Extraer respuesta y fuentes
            answer = result.get('answer', 'No se pudo generar una respuesta.')
            source_docs = result.get('source_documents', [])
            
            print(f"✅ Respuesta generada usando {len(source_docs)} fuentes")
            
            # Opcional: añadir fuentes a la respuesta (solo para depuración)
            if source_docs and len(source_docs) > 0:
                sources = []
                for doc in source_docs[:2]:  # Solo primeras 2 fuentes
                    source = doc.metadata.get('source', 'Desconocido')
                    page = doc.metadata.get('page', 'N/A')
                    sources.append(f"{os.path.basename(source)} (pág. {page})")
                
                # Añadir fuentes a la respuesta (comentado para producción)
                # answer += f"\n\n📚 Fuentes: {', '.join(sources)}"
            
            return answer
            
        except Exception as e:
            error_msg = f"❌ Error al procesar la pregunta: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_document_count(self) -> int:
        """
        Retorna el número de documentos cargados
        
        Returns:
            int: Número de documentos (chunks)
        """
        if self.vectorstore:
            return self.vectorstore._collection.count()
        return 0
    
    def get_document_names(self) -> List[str]:
        """
        Retorna los nombres de los documentos fuente
        
        Returns:
            List[str]: Lista de nombres de archivo únicos
        """
        if not self.vectorstore:
            return []
        
        # Obtener metadatos de todos los documentos
        try:
            collection = self.vectorstore._collection
            if collection.count() > 0:
                metadatas = collection.get()['metadatas']
                sources = set()
                for meta in metadatas:
                    if meta and 'source' in meta:
                        sources.add(os.path.basename(meta['source']))
                return sorted(list(sources))
        except:
            pass
        
        return []
    
    def clear_vectorstore(self):
        """Limpia la base de datos vectorial"""
        self.vectorstore = None
        self.qa_chain = None
        self.memory = None
        
        # Eliminar archivos temporales
        if self.CHROMA_TEMP_DIR.exists():
            shutil.rmtree(self.CHROMA_TEMP_DIR)
            print(f"🧹 Base de datos vectorial eliminada: {self.CHROMA_TEMP_DIR}")
    
    def __del__(self):
        """Destructor: limpia recursos al cerrar"""
        print("\n🧹 Limpiando recursos de RAGEngine...")
        # No eliminamos la base de datos al cerrar para mantener persistencia
        # Si quieres que sea temporal, descomenta la siguiente línea:
        # self.clear_vectorstore()


# Función para pruebas
def test_rag_engine():
    """Prueba el funcionamiento del RAGEngine con ChromaDB"""
    print("🧪 Probando RAGEngine con ChromaDB...")
    
    # Crear archivo de prueba
    test_file = "test_rag.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""DocAssist es un asistente de documentación inteligente.
        Utiliza RAG (Retrieval-Augmented Generation) para responder preguntas.
        Los documentos se procesan y almacenan en ChromaDB.
        Las preguntas se responden usando el contexto de los documentos.
        Este es un documento de prueba para verificar el funcionamiento.""")
    
    try:
        # Probar con Ollama (modelo local)
        print("\n" + "="*50)
        print("Probando con Ollama (modelo local)")
        print("="*50)
        
        engine = RAGEngine(
            provider="Ollama",
            api_key=None,
            model="llama2"  # Asegúrate de tener llama2 descargado
        )
        
        # Cargar documento
        success = engine.load_documents([test_file])
        
        if success:
            print(f"\n📊 Documentos cargados: {engine.get_document_names()}")
            print(f"📊 Total chunks: {engine.get_document_count()}")
            
            # Hacer pregunta
            response = engine.ask("¿Qué es DocAssist?")
            print(f"\n💬 Respuesta:\n{response}")
        
        # Limpiar
        engine.clear_vectorstore()
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(test_file):
            os.remove(test_file)
            print("\n🧹 Archivo temporal eliminado")


if __name__ == "__main__":
    test_rag_engine()