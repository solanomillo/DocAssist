# 📚 DocAssist - Asistente de Documentación Inteligente con RAG
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat&logo=googlegemini&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-UI-FF6F61?style=flat&logo=python&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat&logo=databricks&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat) 

DocAssist es un asistente de escritorio inteligente que utiliza  RAG (Retrieval-Augmented Generation) para responder preguntas basándose exclusivamente en tus documentos locales (PDF y TXT). Con una interfaz moderna y oscura, permite mantener el control total de tus datos y costos.

---

## 📌 Descripción

DocAssist nace de la necesidad de consultar documentación técnica, académica o profesional de forma inteligente, sin depender de conexiones constantes a internet y manteniendo la privacidad de los datos. A diferencia de soluciones en la nube, este asistente:

* Procesa documentos localmente (PDFs y archivos de texto)

* Almacena embeddings en tu máquina con ChromaDB

* Permite múltiples proveedores (Google Gemini, OpenAI, Anthropic, Ollama local)

* Cada sesión es independiente - Nuevos documentos = nuevo contexto

* Gestiona cuotas automáticamente - Pausas inteligentes para APIs gratuitas

Desarrollado con una arquitectura limpia en 3 capas (UI, Core, Config), el proyecto está preparado para uso profesional, académico o personal, priorizando la privacidad y el control de costos.

## **🚀 Stack Tecnológico**

### **🔹 Interfaz de Usuario**
- **tkinter + sv-ttk** - UI moderna con tema oscuro
- **ttk** - Componentes profesionales

### **🔹 Motor RAG y Procesamiento**
- **langchain** - Orquestación de la cadena RAG
- **langchain-chroma** - Base de datos vectorial local
- **langchain-text-splitters** - División inteligente de documentos
- **langchain-google-genai** - Integración con Gemini

### **🔹 Proveedores de IA**
- **google-generativeai** - Google Gemini 2.5
- **langchain-openai** - OpenAI (GPT-4, GPT-3.5)
- **langchain-anthropic** - Anthropic Claude
- **langchain-community** - Ollama (modelos locales)

### **🔹 Procesamiento de Documentos**
- **pypdf** - Extracción de texto de PDFs
- **chromadb** - Base de datos vectorial
- **tiktoken** - Tokenización eficiente

### **🔹 Configuración y Seguridad**
- **python-dotenv** - Gestión de API keys
- **pyinstaller** - Empaquetado a ejecutable

---

## **🧠 Arquitectura del Sistema**

El sistema está diseñado con una arquitectura limpia de 3 capas que separa claramente la interfaz, la lógica de negocio y la configuración:

### **🎯 Capa UI (Interfaz de Usuario)**
- **main_window.py** - Ventana principal con áreas de documentos, chat y progreso
- **settings_dialog.py** - Diálogo de configuración de API con selector de plan
- Feedback visual con barras de progreso y estados
- Tema oscuro moderno con sv-ttk

### **⚙️ Capa Core (Lógica de Negocio)**

**RAG Engine**: Motor principal que coordina:
- Carga y procesamiento de documentos
- Generación de embeddings
- Almacenamiento en ChromaDB
- Consultas con contexto y memoria
- Manejo de cuotas y límites

**Document Loader**: Procesa diferentes formatos:
- 📄 **PDF** - Extracción página por página
- 📝 **TXT** - Carga directa con encoding UTF-8
- División en chunks optimizados (1000 caracteres con 200 de overlap)

### **🔐 Capa Config (Configuración)**
- Gestión segura de API keys en archivo .env
- Persistencia de configuración entre sesiones
- Soporte para múltiples proveedores:
  - **Google Gemini** - Modelos: gemini-2.5-pro, gemini-2.5-flash, gemini-1.5-pro
  - **OpenAI** - gpt-4o, gpt-4o-mini, gpt-4.1
  - **Anthropic** - claude-3-opus, claude-3.5-sonnet, claude-3-haiku
  - **Ollama** - llama3, mistral, phi3, codellama

### **⚙️ Funcionalidades Principales**
- ✅ **Múltiples proveedores** - Gemini, OpenAI, Anthropic y Ollama local
- ✅ **Procesamiento local** - Documentos nunca salen de tu máquina
- ✅ **Sesiones independientes** - Cada carga de documentos empieza desde cero
- ✅ **Manejo inteligente de cuotas** - Pausas automáticas para APIs gratuitas
- ✅ **Feedback visual** - Barras de progreso y estados en tiempo real
- ✅ **Memoria conversacional** - Mantiene contexto entre preguntas
- ✅ **Persistencia de API keys** - Configuración guardada en .env
- ✅ **Modo oscuro** - Interfaz moderna y amigable
- ✅ **Cancelación** - Botón para detener procesamiento largo
- ✅ **Manejo de errores** - Mensajes claros para el usuario
- ✅ **Formato inteligente** - Chunks optimizados para mejor recuperación

---

## 📂 Estructura del Proyecto

```text
DOCASSIST/
├── ui/                          # Capa UI - Interfaz de usuario
│   ├── __init__.py
│   ├── main_window.py           # Ventana principal con áreas de chat/docs
│   └── settings_dialog.py       # Diálogo de configuración de API
│
├── core/                        # Capa Core - Lógica de negocio
│   ├── __init__.py
│   ├── rag_engine.py            # Motor RAG principal
│   └── document_loader.py       # Cargador de PDFs y TXT
│
├── config/                       # Capa Config - Configuración
│   ├── __init__.py
│   └── settings.py               # Gestión de .env y API keys
│
├── assets/                        # Recursos (iconos, etc.)
│   └── icon.ico                   # Icono de la aplicación
│
├── main.py                        # Punto de entrada
├── requirements.txt               # Dependencias
├── .env                           # Configuración (NO versionado)
├── .gitignore                     # Archivos ignorados
└── README.md                       # Este archivo
```

---

## 🛠️ Instalación y Configuración

1️⃣ Clonar el repositorio
```bash
git clone https://github.com/solanomillo/DocAssist.git
cd DocAssist
```

2️⃣ Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

4️⃣ Configurar variables de entorno

Crear un archivo .env en la raíz:

```env
GEMINI_API_KEY=tu_api_key_de_gemini
GEMINI_MODEL=gemini-2.5-flash
```
⚠️ IMPORTANTE: El archivo .env no debe subirse al repositorio (está en .gitignore) y dejarlo vacio la api se ingresa en la interfaz

5️⃣ Ejecutar en modo desarrollo
```bash
python main.py
```
La aplicación se abrirá automáticamente

---

## **🎯 Ejemplos de Uso**

### **📄 Con Gemini (Recomendado para pruebas)**
1. Abre la aplicación
2. Ve a **Opciones → Configurar API**
3. Selecciona "Google Gemini" y plan "Gratuito"
4. Ingresa tu API key y modelo `gemini-2.5-flash`
5. Carga un PDF o TXT
6. ¡Empieza a preguntar!

### **📊 Con OpenAI (Plan de pago)**
- Configura tu API key de OpenAI en el `.env`
- En la aplicación, selecciona "OpenAI" y plan "De Pago"
- Elige modelo como `gpt-4o-mini` (económico)
- Carga documentos y consulta

### **🖥️ Con Ollama (100% local y gratuito)**
1. Instala [Ollama](https://ollama.ai)
2. Descarga un modelo: `ollama pull llama2`
3. En la app, selecciona "Ollama" (no requiere API key)
4. ¡Todo funciona localmente!

---

## **🔐 Seguridad y Privacidad**

✔️ **Sin datos en la nube** - Todo procesamiento es local  
✔️ **API keys seguras** - Guardadas en `.env`, nunca hardcodeadas  
✔️ **Sesiones temporales** - Los documentos se eliminan al cerrar la app  
✔️ **Sin telemetría** - No se envía información de uso  
✔️ **Control de costos** - Límites configurables según plan  
✔️ **Código abierto** - Auditoría completa del código fuente

---

## **⚠️ Manejo de Cuotas y Límites**

### **Plan Gratuito (Gemini)**
- 100 solicitudes/minuto para embeddings
- Procesamiento automático por lotes de 50 chunks
- Pausas de 65 segundos entre lotes
- Mensajes claros cuando se excede la cuota

### **Plan de Pago**
- Lotes de 500 chunks
- Pausas mínimas (1 segundo)
- Mayor capacidad de procesamiento
- Ideal para documentos grandes

---

## **🏗️ Roadmap Futuro**

🔗 **Más formatos** - Soporte para DOCX, HTML, Markdown  
🌐 **Modo web** - Versión SaaS con autenticación  
📊 **Analíticas** - Estadísticas de uso y consultas  
💾 **Historial** - Guardar conversaciones por sesión  
🖼️ **OCR** - Extracción de texto de imágenes en PDFs  
🤖 **Múltiples modelos** - Mezclar proveedores  
📱 **App móvil** - Versión para iOS/Android

---

## **🧪 Pruebas Realizadas**

✅ Carga de PDFs de hasta 81 páginas  
✅ Manejo de límites de cuota gratuita  
✅ Preguntas con contexto y memoria  
✅ Cambio entre proveedores  
✅ Persistencia de configuración  
✅ Compilación exitosa con PyInstaller  
✅ Limpieza de sesiones anteriores

---

## **👨‍💻 Autor**

**Julio Solano**  
🔗 **GitHub:** [https://github.com/solanomillo](https://github.com/solanomillo)  
🔗 **LinkedIn:** [https://www.linkedin.com/in/julio-cesar-solano](https://www.linkedin.com/in/julio-cesar-solano)  
📧 **Email:** [solanomillo144@gmail.com](mailto:solanomillo144@gmail.com)

---

## **📄 Licencia**

Este proyecto está bajo la **Licencia MIT**.  
Podés usarlo, modificarlo y compartirlo libremente, siempre manteniendo la atribución al autor original.

---

⭐ **¿Te gusta el proyecto? ¡No olvides darle una estrella en GitHub!** ⭐
