"""
Motor RAG (Retrieval-Augmented Generation) para DocAssist
Versión compatible con Python 3.12 y LangChain actual
"""

import os
import shutil
import tempfile
from typing import List, Optional
from pathlib import Path

# Importaciones correctas para LangChain actual
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Importaciones específicas por proveedor
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


class RAGEngine:
    """
    Clase principal del motor RAG
    """
    
    CHROMA_TEMP_DIR = Path(tempfile.gettempdir()) / "docassist_chroma"
    
    def __init__(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.chat_history = []
        
        self._setup_provider()
        print(f"✅ RAGEngine inicializado: {self.provider} - {self.model}")
    
    def _setup_provider(self):
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
        # Usar OpenAI para embeddings (requiere API key de OpenAI)
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Anthropic requiere API key de OpenAI para embeddings. Configura OPENAI_API_KEY en tu .env")
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        print(f"🔧 Anthropic configurado con modelo: {self.model}")
    
    def _setup_gemini(self):
        """Configura Google Gemini con los modelos de embeddings correctos"""
        if not self.api_key:
            raise ValueError("API key requerida para Google Gemini")
        
        # Configurar el LLM
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model=self.model,
            temperature=0.7
        )
        print(f"🔧 Google Gemini LLM configurado con modelo: {self.model}")
        
        # --- MODELOS DE EMBEDDINGS CORRECTOS (descubiertos experimentalmente) ---
        embedding_models = [
            "models/gemini-embedding-001",      # Modelo estable
            "models/gemini-embedding-2-preview", # Modelo preview
        ]
        # ----------------------------------------------------------------------
        
        for emb_model in embedding_models:
            try:
                print(f"🔄 Configurando embeddings con: {emb_model}")
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    google_api_key=self.api_key,
                    model=emb_model
                )
                # Verificar que funciona
                test_vec = self.embeddings.embed_query("test")
                if test_vec and len(test_vec) > 0:
                    print(f"✅ Embeddings funcionando correctamente con: {emb_model}")
                    return
            except Exception as e:
                print(f"   ⚠️ Error con {emb_model}: {str(e)[:100]}...")
                continue
        
        # Si llegamos aquí, ningún embedding funcionó
        raise Exception(
            f"No se pudo configurar embeddings para Gemini. "
            f"Modelos probados: {embedding_models}. "
            f"Ejecuta test_gemini_models.py para diagnosticar."
        )
    
    def _setup_ollama(self):
        self.llm = Ollama(model=self.model, temperature=0.7)
        self.embeddings = OllamaEmbeddings(model=self.model)
        print(f"🔧 Ollama configurado con modelo local: {self.model}")
    
    def load_documents(self, file_paths: List[str]) -> bool:
        """Carga documentos con prints de depuración"""
        try:
            print(f"\n📚 ===== INICIANDO CARGA DE DOCUMENTOS =====")
            print(f"📚 Procesando {len(file_paths)} documento(s)...")
            
            # 1. Procesar documentos
            print("📚 Paso 1: Procesando documentos...")
            chunks = self._process_documents(file_paths)
            print(f"📚 Paso 1 completado: {len(chunks)} chunks generados")
            
            if not chunks:
                print("❌ No se pudieron procesar los documentos")
                return False
            
            # 2. Crear vectorstore
            print("📚 Paso 2: Creando base de datos vectorial...")
            print(f"📚 Usando embeddings: {self.embeddings}")
            
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(self.CHROMA_TEMP_DIR)
            )
            print(f"📚 Paso 2 completado: Vectorstore creado")
            
            print(f"✅ {len(chunks)} chunks procesados correctamente")
            print(f"📚 ===== CARGA COMPLETADA =====\n")
            return True
        
        except Exception as e:
            print(f"❌ Error cargando documentos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _process_documents(self, file_paths: List[str]) -> List[Document]:
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
        """Realiza una pregunta con prints de depuración"""
        if self.vectorstore is None:
            return "⚠️ No hay documentos cargados. Por favor, carga algunos documentos primero."
        
        try:
            print(f"\n❓ ===== PROCESANDO PREGUNTA =====")
            print(f"❓ Pregunta: {question}")
            
            # Crear retriever
            print("📚 Paso 1: Creando retriever...")
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
            
            # Obtener documentos relevantes
            print("📚 Paso 2: Buscando documentos relevantes...")
            docs = retriever.invoke(question)
            print(f"📚 Paso 2 completado: {len(docs)} documentos encontrados")
            
            # Construir contexto
            context = "\n\n".join([doc.page_content for doc in docs])
            print(f"📚 Contexto generado: {len(context)} caracteres")
            
            # Construir prompt
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
            
            print("🤖 Paso 3: Invocando LLM...")
            response = self.llm.invoke(prompt)
            
            answer = response.content if hasattr(response, 'content') else str(response)
            self.chat_history.append((question, answer))
            
            print(f"✅ Respuesta generada: {len(answer)} caracteres")
            print(f"❓ ===== PREGUNTA COMPLETADA =====\n")
            
            return answer
            
        except Exception as e:
            error_msg = f"❌ Error al procesar la pregunta: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
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
    
    def clear_vectorstore(self):
        self.vectorstore = None
        self.chat_history = []
        if self.CHROMA_TEMP_DIR.exists():
            shutil.rmtree(self.CHROMA_TEMP_DIR)
            print(f"🧹 Base de datos vectorial eliminada")
    
    def __del__(self):
        pass


if __name__ == "__main__":
    print("✅ RAGEngine cargado correctamente")