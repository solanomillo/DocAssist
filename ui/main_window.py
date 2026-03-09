"""
Ventana principal de la aplicación DocAssist
Contiene todas las áreas de la interfaz: menú, documentos, chat y entrada de preguntas
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class RAGAssistantApp:
    """
    Clase principal de la interfaz gráfica
    Maneja toda la interacción con el usuario
    """
    
    def __init__(self, root):
        """
        Inicializa la ventana principal con todas sus áreas
        
        Args:
            root: Ventana raíz de Tkinter
        """
        self.root = root
        self.root.title("DocAssist - Asistente de Documentos")
        self.root.geometry("900x600")
        
        # Configurar color de fondo modo oscuro
        self.root.configure(bg='#2b2b2b')
        
        # Configurar el grid para que sea responsive
        self.root.grid_rowconfigure(1, weight=1)  # Fila del chat se expande
        self.root.grid_rowconfigure(2, weight=0)  # Fila de entrada no se expande
        self.root.grid_columnconfigure(0, weight=1)  # Columna única se expande
        
        # Crear menú superior
        self.create_menu()
        
        # Crear marco superior para documentos y chat
        self.create_main_area()
        
        # Crear área de entrada de preguntas
        self.create_question_area()
        
        # Centrar la ventana en la pantalla
        self.center_window()
        
        # Vincular evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Mostrar mensaje de bienvenida
        self.add_to_chat("Sistema", "👋 Bienvenido a DocAssist. Configura tu API en Opciones > Configurar API para comenzar.")
    
    def create_menu(self):
        """Crea la barra de menú superior"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Salir", command=self.on_closing, accelerator="Alt+F4")
        
        # Menú Opciones
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=options_menu)
        options_menu.add_command(label="Configurar API", command=self.open_settings, accelerator="Ctrl+,")
    
    def create_main_area(self):
        """Crea el área principal dividida en documentos y chat"""
        # Frame contenedor para las dos áreas
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        
        # Configurar grid del main_frame
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)  # Chat ocupa 3/4
        main_frame.grid_columnconfigure(0, weight=1)  # Documentos ocupa 1/4
        
        # --- ÁREA DE DOCUMENTOS (izquierda) ---
        docs_frame = ttk.LabelFrame(main_frame, text="📄 Documentos Cargados", padding=5)
        docs_frame.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='nsew')
        
        # Configurar grid del docs_frame
        docs_frame.grid_rowconfigure(0, weight=1)
        docs_frame.grid_columnconfigure(0, weight=1)
        
        # Listbox para mostrar documentos
        self.docs_listbox = tk.Listbox(
            docs_frame,
            bg='#3c3c3c',
            fg='#ffffff',
            selectbackground='#4a4a4a',
            selectforeground='#ffffff',
            font=('Arial', 10)
        )
        self.docs_listbox.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        # Scrollbar para el listbox
        docs_scrollbar = ttk.Scrollbar(docs_frame, orient='vertical', command=self.docs_listbox.yview)
        docs_scrollbar.grid(row=0, column=1, sticky='ns')
        self.docs_listbox.config(yscrollcommand=docs_scrollbar.set)
        
        # Botón para cargar documentos
        self.load_btn = ttk.Button(
            docs_frame,
            text="📂 Cargar Documentos",
            command=self.load_documents
        )
        self.load_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # --- ÁREA DE CHAT (derecha) ---
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Conversación", padding=5)
        chat_frame.grid(row=0, column=1, padx=(5, 0), pady=5, sticky='nsew')
        
        # Configurar grid del chat_frame
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        # Área de chat con scroll (ScrolledText)
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state='disabled',
            bg='#1e1e1e',
            fg='#d4d4d4',
            font=('Arial', 10),
            insertbackground='#ffffff'  # Color del cursor
        )
        self.chat_display.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        # Configurar tags para colores en el chat
        self.chat_display.tag_config('system', foreground='#888888')
        self.chat_display.tag_config('user', foreground='#4ec9b0')
        self.chat_display.tag_config('assistant', foreground='#ce9178')
        self.chat_display.tag_config('error', foreground='#f44747')
    
    def create_question_area(self):
        """Crea el área inferior para escribir preguntas"""
        # Frame contenedor
        question_frame = tk.Frame(self.root, bg='#2b2b2b')
        question_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        
        # Configurar grid del question_frame
        question_frame.grid_columnconfigure(0, weight=1)
        
        # Campo de entrada para la pregunta
        self.question_entry = ttk.Entry(
            question_frame,
            font=('Arial', 10)
        )
        self.question_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        # Vincular tecla Enter para enviar pregunta
        self.question_entry.bind('<Return>', lambda e: self.ask_question())
        
        # Botón para enviar pregunta
        self.ask_btn = ttk.Button(
            question_frame,
            text="📤 Enviar",
            command=self.ask_question,
            state='disabled'  # Inicialmente deshabilitado
        )
        self.ask_btn.grid(row=0, column=1)
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def add_to_chat(self, sender, message):
        """
        Añade un mensaje al área de chat
        
        Args:
            sender: Quién envía el mensaje ('Sistema', 'Usuario', 'Asistente')
            message: Contenido del mensaje
        """
        self.chat_display.config(state='normal')
        
        # Determinar tag según el remitente
        if sender.lower() == 'sistema':
            tag = 'system'
            prefix = '🔧'
        elif sender.lower() == 'usuario':
            tag = 'user'
            prefix = '👤'
        elif sender.lower() == 'asistente':
            tag = 'assistant'
            prefix = '🤖'
        else:
            tag = 'system'
            prefix = '📌'
        
        # Formatear y insertar el mensaje
        formatted_message = f"{prefix} {sender}: {message}\n\n"
        self.chat_display.insert(tk.END, formatted_message, tag)
        
        # Auto-scroll al final
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def load_documents(self):
        """Manejador para cargar documentos"""
        # Por ahora solo muestra un mensaje
        messagebox.showinfo(
            "Cargar Documentos",
            "Funcionalidad en desarrollo.\n\nPróximamente podrás cargar PDFs y archivos de texto."
        )
        self.add_to_chat("Sistema", "ℹ️ Función de carga de documentos en desarrollo")
    
    def ask_question(self):
        """Manejador para hacer preguntas"""
        question = self.question_entry.get().strip()
        
        if not question:
            messagebox.showwarning("Pregunta vacía", "Por favor, escribe una pregunta.")
            return
        
        # Mostrar la pregunta del usuario
        self.add_to_chat("Usuario", question)
        
        # Limpiar campo de entrada
        self.question_entry.delete(0, tk.END)
        
        # Simular respuesta (placeholder)
        self.root.after(1000, lambda: self.simulate_response(question))
    
    def simulate_response(self, question):
        """
        Simula una respuesta del asistente (temporal)
        
        Args:
            question: Pregunta del usuario
        """
        response = f"🔧 Funcionalidad en desarrollo. Tu pregunta fue: '{question}'\n\nPróximamente recibirás respuestas basadas en tus documentos usando IA."
        self.add_to_chat("Asistente", response)
    
    def open_settings(self):
        """Abre el diálogo de configuración de API"""
        messagebox.showinfo(
            "Configurar API",
            "Funcionalidad en desarrollo.\n\nPróximamente podrás configurar:\n"
            "• OpenAI\n• Anthropic\n• Google Gemini\n• Ollama (local)"
        )
        self.add_to_chat("Sistema", "ℹ️ Función de configuración de API en desarrollo")
    
    def on_closing(self):
        """Maneja el evento de cierre de la ventana"""
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir de DocAssist?"):
            print("Cerrando DocAssist...")
            self.root.destroy()


# Función para pruebas independientes
def test_window():
    """Función para probar la ventana directamente"""
    root = tk.Tk()
    app = RAGAssistantApp(root)
    root.mainloop()


if __name__ == "__main__":
    test_window()