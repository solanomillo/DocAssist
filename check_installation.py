"""
Script para verificar que todas las importaciones y dependencias están correctas
Ejecutar con: python check_installation.py
"""

import sys
print(f"🔍 Verificando instalación...")
print(f"Python version: {sys.version}\n")

# Lista de módulos a verificar
modules_to_check = [
    ("langchain_community.vectorstores", "Chroma"),
    ("langchain_community.document_loaders", "PyPDFLoader"),
    ("langchain_community.llms", "Ollama"),
    ("langchain_community.embeddings", "OllamaEmbeddings"),
    ("langchain_text_splitters", "RecursiveCharacterTextSplitter"),
    ("langchain_core.documents", "Document"),
    ("langchain_openai", "ChatOpenAI"),
    ("langchain_anthropic", "ChatAnthropic"),
    ("langchain_google_genai", "ChatGoogleGenerativeAI"),
]

print("📦 Verificando imports:")
for module_name, class_name in modules_to_check:
    try:
        module = __import__(module_name, fromlist=[class_name])
        print(f"   ✅ {module_name}.{class_name}")
    except ImportError as e:
        print(f"   ❌ {module_name}.{class_name}: {e}")

print("\n" + "="*50)
print("Para probar Gemini y ver modelos disponibles:")
print("python test_gemini_models.py")
print("="*50)