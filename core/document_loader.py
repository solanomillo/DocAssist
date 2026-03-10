"""
Cargador de documentos para DocAssist
Maneja la carga y procesamiento de diferentes tipos de archivos
"""

import os
from typing import List, Optional
from pathlib import Path

# Importaciones correctas de LangChain
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document  # CORREGIDO: langchain_core.documents en lugar de langchain.schema


class DocumentLoader:
    """
    Clase para cargar y procesar documentos de diferentes formatos
    Soporta: PDF, TXT
    """
    
    # Tamaño de chunk y overlap configurables
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        """
        Inicializa el cargador de documentos
        
        Args:
            chunk_size: Tamaño de cada fragmento de texto
            chunk_overlap: Solapamiento entre fragmentos
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Inicializar el divisor de texto
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Carga un documento individual según su extensión
        
        Args:
            file_path: Ruta al archivo a cargar
            
        Returns:
            List[Document]: Lista de documentos (páginas o fragmentos)
        """
        file_path = str(file_path)  # Asegurar que es string
        extension = Path(file_path).suffix.lower()
        
        print(f"📄 Cargando: {Path(file_path).name}")
        
        try:
            if extension == '.pdf':
                return self._load_pdf(file_path)
            elif extension == '.txt':
                return self._load_text(file_path)
            else:
                print(f"⚠️ Formato no soportado: {extension}")
                return []
                
        except Exception as e:
            print(f"❌ Error cargando {file_path}: {e}")
            return []
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """
        Carga un archivo PDF usando PyPDFLoader
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            List[Document]: Lista de documentos (una por página)
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Añadir metadatos útiles
        for i, doc in enumerate(documents):
            doc.metadata['source'] = file_path
            doc.metadata['page'] = i + 1
            doc.metadata['type'] = 'pdf'
        
        print(f"   📑 {len(documents)} páginas cargadas")
        return documents
    
    def _load_text(self, file_path: str) -> List[Document]:
        """
        Carga un archivo de texto usando TextLoader
        
        Args:
            file_path: Ruta al archivo de texto
            
        Returns:
            List[Document]: Lista con un documento
        """
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        
        # Añadir metadatos
        for doc in documents:
            doc.metadata['source'] = file_path
            doc.metadata['type'] = 'txt'
        
        print(f"   📝 {len(documents)} documento(s) de texto")
        return documents
    
    def load_multiple_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Carga múltiples documentos
        
        Args:
            file_paths: Lista de rutas a archivos
            
        Returns:
            List[Document]: Lista combinada de todos los documentos
        """
        all_documents = []
        
        for file_path in file_paths:
            documents = self.load_document(file_path)
            all_documents.extend(documents)
        
        print(f"\n📚 Total: {len(all_documents)} páginas/fragmentos cargados de {len(file_paths)} archivos")
        return all_documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Divide los documentos en chunks más pequeños
        
        Args:
            documents: Lista de documentos a dividir
            
        Returns:
            List[Document]: Documentos divididos en chunks
        """
        if not documents:
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        print(f"✂️  Divididos en {len(chunks)} chunks (tamaño: {self.chunk_size}, overlap: {self.chunk_overlap})")
        
        return chunks
    
    def process_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Procesa documentos completos: carga y divide
        
        Args:
            file_paths: Lista de rutas a archivos
            
        Returns:
            List[Document]: Documentos procesados y divididos
        """
        # Cargar documentos
        documents = self.load_multiple_documents(file_paths)
        
        if not documents:
            return []
        
        # Dividir en chunks
        chunks = self.split_documents(documents)
        
        return chunks


# Función para pruebas
def test_document_loader():
    """Prueba el cargador de documentos"""
    print("🧪 Probando DocumentLoader...")
    
    # Crear un archivo de prueba temporal
    test_file = "test_doc.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Este es un documento de prueba.\n" * 50)
    
    try:
        # Inicializar cargador
        loader = DocumentLoader(chunk_size=200, chunk_overlap=50)
        
        # Procesar documento
        chunks = loader.process_documents([test_file])
        
        print(f"\n✅ Documento procesado:")
        print(f"   • Total chunks: {len(chunks)}")
        
        if chunks:
            print(f"   • Primer chunk: {chunks[0].page_content[:100]}...")
            print(f"   • Metadatos: {chunks[0].metadata}")
        
    finally:
        # Limpiar archivo temporal
        if os.path.exists(test_file):
            os.remove(test_file)
            print("\n🧹 Archivo temporal eliminado")


if __name__ == "__main__":
    test_document_loader()