"""
Script para descubrir qué modelos de embeddings están disponibles en Google Gemini
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar API key del .env
load_dotenv()
api_key = os.getenv("DOCASSIST_API_KEY")

if not api_key:
    api_key = input("Ingresa tu API key de Google Gemini: ")

# Configurar la API
genai.configure(api_key=api_key)

print("\n" + "="*60)
print("📋 MODELOS DISPONIBLES EN GOOGLE GEMINI")
print("="*60)

# Listar todos los modelos
print("\n🔍 TODOS LOS MODELOS:")
for model in genai.list_models():
    print(f"  - {model.name}")
    print(f"    Métodos: {model.supported_generation_methods}")

# Filtrar modelos de embeddings
print("\n" + "="*60)
print("🎯 MODELOS DE EMBEDDINGS:")
print("="*60)

embedding_models = []
for model in genai.list_models():
    if 'embed' in model.name.lower() or 'embedding' in model.name.lower():
        embedding_models.append(model.name)
        print(f"  ✅ {model.name}")
        print(f"     Métodos: {model.supported_generation_methods}")

print("\n" + "="*60)
print(f"📌 Total de modelos de embeddings encontrados: {len(embedding_models)}")
print("="*60)

if embedding_models:
    print("\n💡 RECOMENDACIÓN: Usa estos modelos en tu código:")
    for model in embedding_models:
        print(f'    "{model}",')