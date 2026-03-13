"""
Ventana principal de la aplicación DocAssist - Versión mejorada
Contiene barra de progreso, tema moderno, manejo de cuotas y mejor feedback visual
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sv_ttk
import os
import threading
from datetime import datetime

from ui.settings_dialog import SettingsDialog
from config.settings import ConfigManager
from core.rag_engine import RAGEngine, QuotaExceededError


class RAGAssistantApp:
    """
    Clase principal de la interfaz gráfica - Versión con feedback visual mejorado
    y manejo de cuotas de API
    """
    
    def __init__(self, root):
        """
        Inicializa la ventana principal con tema moderno
        """
        self.root = root
        self.root.title("DocAssist - Asistente de Documentos")
        self.root.geometry("1000x650")
        
        # Aplicar tema moderno (oscuro)
        sv_ttk.set_theme("dark")
        
        # Inicializar gestor de configuración
        self.config_manager = ConfigManager()
        
        # Variables
        self.api_provider = None
        self.api_key = None
        self.api_model = None
        self.api_plan = "free"  # 'free' o 'paid'
        self.rag_engine = None
        self.is_processing = False
        
        # Configurar grid principal
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Crear interfaz
        self.create_menu()
        self.create_main_area()
        self.create_status_bar()
        self.create_question_area()
        
        # Centrar ventana
        self.center_window()
        
        # Vincular cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Cargar configuración
        self.load_saved_configuration()
        
        # Mostrar bienvenida
        self.add_to_chat("Sistema", "👋 Bienvenido a DocAssist. Configura tu API en Opciones > Configurar API para comenzar.")
    
    def create_menu(self):
        """Crea la barra de menú superior"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Limpiar configuración", command=self.clear_configuration)
        file_menu.add_command(label="Limpiar base de datos", command=self.clear_vectorstore)
        file_menu.add_command(label="Limpiar CACHÉ completo", command=self.clear_all_cache)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing, accelerator="Alt+F4")
        
        # Menú Opciones
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=options_menu)
        options_menu.add_command(label="Configurar API", command=self.open_settings, accelerator="Ctrl+,")
    
    def create_main_area(self):
        """Crea el área principal con barra de progreso"""
        # Frame contenedor
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # --- BARRA DE PROGRESO (inicialmente oculta) ---
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky='ew')
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=100
        )
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="",
            font=('Arial', 9)
        )
        self.progress_label.pack(side='right')
        
        # Ocultar barra de progreso inicialmente
        self.progress_frame.grid_remove()
        
        # --- ÁREA DE DOCUMENTOS ---
        docs_frame = ttk.LabelFrame(main_frame, text="📄 Documentos Cargados", padding=10)
        docs_frame.grid(row=1, column=0, padx=(0, 5), pady=5, sticky='nsew')
        
        docs_frame.grid_rowconfigure(0, weight=1)
        docs_frame.grid_columnconfigure(0, weight=1)
        
        # Listbox con scrollbar
        listbox_frame = ttk.Frame(docs_frame)
        listbox_frame.grid(row=0, column=0, sticky='nsew')
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        
        self.docs_listbox = tk.Listbox(
            listbox_frame,
            bg='#2b2b2b',
            fg='#ffffff',
            selectbackground='#404040',
            selectforeground='#ffffff',
            font=('Arial', 10),
            relief='flat'
        )
        self.docs_listbox.grid(row=0, column=0, sticky='nsew')
        
        docs_scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.docs_listbox.yview)
        docs_scrollbar.grid(row=0, column=1, sticky='ns')
        self.docs_listbox.config(yscrollcommand=docs_scrollbar.set)
        
        # Botón de carga
        self.load_btn = ttk.Button(
            docs_frame,
            text="📂 Cargar Documentos",
            command=self.load_documents,
            style='Accent.TButton'
        )
        self.load_btn.grid(row=1, column=0, pady=(10, 0), sticky='ew')
        
        # --- ÁREA DE CHAT ---
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Conversación", padding=10)
        chat_frame.grid(row=1, column=1, padx=(5, 0), pady=5, sticky='nsew')
        
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        # Área de chat mejorada
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state='disabled',
            bg='#1e1e1e',
            fg='#d4d4d4',
            font=('Arial', 10),
            insertbackground='#ffffff',
            relief='flat',
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        
        # Tags de color
        self.chat_display.tag_config('system', foreground='#888888', font=('Arial', 9, 'italic'))
        self.chat_display.tag_config('user', foreground='#4ec9b0', font=('Arial', 10, 'bold'))
        self.chat_display.tag_config('assistant', foreground='#ce9178', font=('Arial', 10))
        self.chat_display.tag_config('error', foreground='#f44747', font=('Arial', 10, 'bold'))
        self.chat_display.tag_config('success', foreground='#6a9955', font=('Arial', 10, 'bold'))
        self.chat_display.tag_config('info', foreground='#4fc1ff', font=('Arial', 9))
        self.chat_display.tag_config('warning', foreground='#d98e2e', font=('Arial', 10, 'bold'))
        self.chat_display.tag_config('thinking', foreground='#888888', font=('Arial', 9, 'italic'))
    
    def create_status_bar(self):
        """Crea la barra de estado inferior"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="✅ Listo",
            font=('Arial', 9)
        )
        self.status_label.pack(side='left')
        
        self.provider_status = ttk.Label(
            self.status_frame,
            text="⚙️ Sin configurar",
            font=('Arial', 9)
        )
        self.provider_status.pack(side='right')
        
        self.plan_status = ttk.Label(
            self.status_frame,
            text="",
            font=('Arial', 9),
            foreground='#888888'
        )
        self.plan_status.pack(side='right', padx=(0, 10))
    
    def create_question_area(self):
        """Crea el área de pregunta mejorada"""
        question_frame = ttk.Frame(self.root)
        question_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        
        question_frame.grid_columnconfigure(0, weight=1)
        
        # Campo de texto
        self.question_entry = ttk.Entry(
            question_frame,
            font=('Arial', 10)
        )
        self.question_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        self.question_entry.bind('<Return>', lambda e: self.ask_question())
        
        # Botón enviar
        self.ask_btn = ttk.Button(
            question_frame,
            text="📤 Enviar",
            command=self.ask_question,
            state='disabled'
        )
        self.ask_btn.grid(row=0, column=1)
    
    def center_window(self):
        """Centra la ventana"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def add_to_chat(self, sender, message, tag_override=None):
        """
        Añade mensaje al chat con formato mejorado
        """
        self.chat_display.config(state='normal')
        
        if tag_override:
            tag = tag_override
        elif sender.lower() == 'sistema':
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
        
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        
        if not tag_override:
            formatted_message = f"{timestamp}{prefix} {sender}: {message}\n\n"
        else:
            formatted_message = f"{timestamp}{message}\n\n"
        
        self.chat_display.insert(tk.END, formatted_message, tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def show_progress(self, message="Procesando..."):
        """Muestra la barra de progreso"""
        self.progress_label.config(text=message)
        self.progress_bar['value'] = 0
        self.progress_frame.grid()
        self.root.update()
    
    def hide_progress(self):
        """Oculta la barra de progreso"""
        self.progress_frame.grid_remove()
        self.root.update()
    
    def update_progress(self, percent, message):
        """Actualiza la barra de progreso (puede llamarse desde hilos)"""
        self.progress_bar['value'] = percent
        self.progress_label.config(text=message)
        self.root.update()
    
    def update_status(self, message, is_error=False):
        """Actualiza la barra de estado"""
        self.status_label.config(text=message)
        if is_error:
            self.status_label.config(foreground='#f44747')
        else:
            self.status_label.config(foreground='')
    
    def load_saved_configuration(self):
        """Carga configuración guardada"""
        config = self.config_manager.load_api_config()
        if config:
            self.api_provider = config['provider']
            self.api_key = config['api_key']
            self.api_model = config['model']
            self.api_plan = config.get('plan', 'free')
            self.create_rag_engine()
            
            plan_text = "GRATIS" if self.api_plan == "free" else "PAGO"
            self.provider_status.config(text=f"⚙️ {self.api_provider} - {self.api_model}")
            self.plan_status.config(text=f"📊 {plan_text}")
            self.add_to_chat("Sistema", 
                f"⚙️ Configuración cargada: {self.api_provider} - {self.api_model} ({plan_text})", 
                'success')
    
    def create_rag_engine(self):
        """Crea el motor RAG con el plan seleccionado"""
        try:
            self.show_progress("Inicializando motor RAG...")
            
            self.rag_engine = RAGEngine(
                provider=self.api_provider,
                api_key=self.api_key,
                model=self.api_model,
                is_paid_plan=(self.api_plan == "paid")
            )
            
            self.hide_progress()
            
            plan_text = "PAGO" if self.api_plan == "paid" else "GRATIS"
            self.update_status(f"✅ Listo - {self.api_provider}")
            self.plan_status.config(text=f"📊 {plan_text}")
            self.add_to_chat("Sistema", f"🤖 Motor RAG inicializado (Plan {plan_text})", 'info')
            
        except Exception as e:
            self.hide_progress()
            self.update_status(f"❌ Error: {str(e)[:50]}...", True)
            self.add_to_chat("Sistema", f"❌ Error al inicializar motor: {str(e)}", 'error')
            self.rag_engine = None
    
    def open_settings(self):
        """Abre el diálogo de configuración de API"""
        dialog = SettingsDialog(self.root)
        self.root.wait_window(dialog)
        
        if dialog.result:
            self.api_provider = dialog.result['provider']
            self.api_key = dialog.result['api_key']
            self.api_model = dialog.result['model']
            self.api_plan = dialog.result.get('plan', 'free')
            
            try:
                # Guardar configuración
                self.config_manager.save_api_config(
                    provider=self.api_provider,
                    api_key=self.api_key,
                    model=self.api_model,
                    plan=self.api_plan
                )
                
                # Crear motor RAG
                self.create_rag_engine()
                
                # Actualizar UI
                plan_text = "PAGO" if self.api_plan == "paid" else "GRATIS"
                self.provider_status.config(text=f"⚙️ {self.api_provider} - {self.api_model}")
                self.plan_status.config(text=f"📊 {plan_text}")
                self.add_to_chat("Sistema", 
                    f"✅ API configurada: {self.api_provider} - {self.api_model} ({plan_text})", 
                    'success')
                    
            except QuotaExceededError as e:
                self.add_to_chat("Sistema", f"⚠️ {str(e)}", 'warning')
                messagebox.showwarning("Límite de cuota", str(e))
            except Exception as e:
                self.add_to_chat("Sistema", f"❌ Error: {str(e)}", 'error')
                messagebox.showerror("Error", f"Error al configurar API:\n{str(e)}")
        else:
            self.add_to_chat("Sistema", "ℹ️ Configuración cancelada", 'info')
    
    def load_documents(self):
        """Carga documentos - SIEMPRE EMPIEZA DESDE CERO"""
        if not self.rag_engine:
            messagebox.showinfo("Info", "Configura una API primero")
            return
        
        # Ya no preguntamos, siempre empezamos desde cero
        # Pero avisamos al usuario que los anteriores se borrarán
        if self.docs_listbox.size() > 0:
            if not messagebox.askyesno(
                "Confirmar",
                "Al cargar nuevos documentos, los anteriores se eliminarán.\n\n"
                "¿Quieres continuar?"
            ):
                return
        
        files = filedialog.askopenfilenames(
            title="Seleccionar documentos",
            filetypes=[("Documentos", "*.pdf *.txt"), ("PDF", "*.pdf"), ("Texto", "*.txt")]
        )
        
        if not files:
            return
        
        # Crear ventana de progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Procesando documentos")
        progress_window.geometry("450x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Centrar
        progress_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (450 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (200 // 2)
        progress_window.geometry(f'+{x}+{y}')
        
        # Widgets
        ttk.Label(progress_window, text="Procesando documentos...", font=('Arial', 10, 'bold')).pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=400)
        progress_bar.pack(pady=10)
        
        status_label = ttk.Label(progress_window, text="Iniciando...", wraplength=400)
        status_label.pack(pady=5)
        
        # Frame para botones
        button_frame = ttk.Frame(progress_window)
        button_frame.pack(pady=10)
        
        cancel_btn = ttk.Button(
            button_frame, 
            text="Cancelar",
            command=lambda: self.cancel_processing(progress_window)
        )
        cancel_btn.pack(side='left', padx=5)
        
        # Deshabilitar botón principal
        self.load_btn.config(state='disabled')
        self.ask_btn.config(state='disabled')
        
        def update_progress(percent, message):
            """Actualiza la barra de progreso (llamado desde otro hilo)"""
            progress_bar['value'] = percent
            status_label.config(text=message)
            progress_window.update()
        
        def process():
            try:
                # Llamar al motor - SIEMPRE empieza desde cero
                success = self.rag_engine.load_documents(
                    list(files), 
                    progress_callback=update_progress
                )
                
                if success:
                    self.root.after(0, lambda f=files, w=progress_window: self._on_documents_loaded(f, w))
                else:
                    self.root.after(0, lambda w=progress_window: self._on_documents_cancelled(w))
                    
            except QuotaExceededError as e:
                error_msg = str(e)
                self.root.after(0, lambda err=error_msg, w=progress_window: self._on_quota_error(err, w))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda err=error_msg, w=progress_window: self._on_documents_error(err, w))
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
        
    def cancel_processing(self, window):
        """Cancela el procesamiento en curso"""
        if self.rag_engine:
            self.rag_engine.cancel_processing()
            window.destroy()
            self.load_btn.config(state='normal')
            self.add_to_chat("Sistema", "⏹️ Procesamiento cancelado por el usuario", 'system')
    
    def _on_documents_loaded(self, files, window):
        """Callback cuando se cargan documentos exitosamente"""
        window.destroy()
        self.load_btn.config(state='normal')
        
        # Limpiar lista ANTES de agregar nuevos (por si acaso)
        self.docs_listbox.delete(0, tk.END)
        
        # Agregar nuevos documentos
        for f in files:
            self.docs_listbox.insert(tk.END, f"📄 {os.path.basename(f)}")
        
        self.ask_btn.config(state='normal')
        self.update_status(f"✅ {len(files)} documento(s) cargado(s)")
        self.add_to_chat("Sistema", f"✅ {len(files)} documento(s) cargado(s) - Nueva sesión", 'success')
        
    def _on_quota_error(self, error_msg, window):
        """Maneja error de cuota"""
        window.destroy()
        self.load_btn.config(state='normal')
        
        self.add_to_chat("Sistema", f"⚠️ Límite de cuota: {error_msg[:200]}...", 'warning')
        
        # Mostrar mensaje detallado
        messagebox.showerror(
            "Límite de cuota excedido",
            f"{error_msg}\n\n"
            "💡 Sugerencias:\n"
            "• Espera unos minutos y vuelve a intentar\n"
            "• Cambia a plan de pago en Configuración\n"
            "• Procesa documentos más pequeños\n"
            "• Usa Ollama local para embeddings gratuitos"
        )
    
    def _on_documents_cancelled(self, window):
        """Maneja cancelación"""
        window.destroy()
        self.load_btn.config(state='normal')
        self.add_to_chat("Sistema", "⏹️ Carga cancelada", 'system')
    
    def _on_documents_error(self, error_msg, window):
        """Maneja error general"""
        window.destroy()
        self.load_btn.config(state='normal')
        messagebox.showerror("Error", f"Error al cargar documentos:\n{error_msg}")
        self.add_to_chat("Sistema", f"❌ Error: {error_msg[:100]}...", 'error')
    
    def ask_question(self):
        """Hace pregunta con feedback"""
        if not self.rag_engine or self.is_processing:
            return
        
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Advertencia", "Escribe una pregunta")
            return
        
        # Mostrar pregunta
        self.add_to_chat("Usuario", question)
        self.question_entry.delete(0, tk.END)
        
        # Deshabilitar controles
        self.is_processing = True
        self.ask_btn.config(state='disabled')
        self.question_entry.config(state='disabled')
        self.update_status("Procesando pregunta...")
        
        # Mostrar pensando
        self.add_to_chat("Asistente", "🤔 Pensando...", 'thinking')
        
        def process():
            try:
                response = self.rag_engine.ask(question)
                self.root.after(0, lambda: self._on_answer_received(response))
            except Exception as e:
                self.root.after(0, lambda: self._on_answer_error(e))
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def _on_answer_received(self, response):
        """Callback cuando llega la respuesta"""
        # Eliminar mensaje de pensando
        self.remove_last_message()
        self.add_to_chat("Asistente", response)
        
        # Rehabilitar controles
        self.is_processing = False
        self.ask_btn.config(state='normal')
        self.question_entry.config(state='normal')
        self.question_entry.focus()
        self.update_status("✅ Listo")
    
    def _on_answer_error(self, error):
        """Callback cuando hay error"""
        self.remove_last_message()
        error_msg = str(error)
        self.add_to_chat("Sistema", f"❌ Error: {error_msg[:200]}...", 'error')
        
        self.is_processing = False
        self.ask_btn.config(state='normal')
        self.question_entry.config(state='normal')
        self.update_status("❌ Error", True)
    
    def remove_last_message(self):
        """Elimina último mensaje del chat"""
        self.chat_display.config(state='normal')
        content = self.chat_display.get("1.0", tk.END)
        messages = content.split("\n\n")
        if len(messages) > 2:
            new_content = "\n\n".join(messages[:-2]) + "\n\n"
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.insert("1.0", new_content)
        self.chat_display.config(state='disabled')
    
    def clear_configuration(self):
        """Limpia configuración guardada"""
        if messagebox.askyesno("Confirmar", "¿Eliminar configuración de API?"):
            self.api_provider = None
            self.api_key = None
            self.api_model = None
            self.api_plan = "free"
            self.rag_engine = None
            self.config_manager.clear_api_config()
            self.provider_status.config(text="⚙️ Sin configurar")
            self.plan_status.config(text="")
            self.add_to_chat("Sistema", "🗑️ Configuración eliminada", 'system')
    
    def clear_vectorstore(self):
        """Limpia base de datos vectorial"""
        if self.rag_engine and messagebox.askyesno("Confirmar", "¿Eliminar base de datos vectorial?"):
            self.rag_engine.clear_vectorstore()
            self.docs_listbox.delete(0, tk.END)
            self.ask_btn.config(state='disabled')
            self.add_to_chat("Sistema", "🧹 Base de datos vectorial eliminada", 'info')
    
    def clear_all_cache(self):
        """Limpia todo el caché de documentos anteriores"""
        if messagebox.askyesno(
            "Confirmar", 
            "¿Eliminar todo el caché de documentos anteriores?\n\n"
            "Esto borrará los embeddings de sesiones previas.\n"
            "La próxima vez que cargues documentos será desde cero."
        ):
            if self.rag_engine:
                self.rag_engine.clear_vectorstore()
            self.docs_listbox.delete(0, tk.END)
            self.ask_btn.config(state='disabled')
            self.add_to_chat("Sistema", "🧹 Caché de documentos eliminado completamente", 'success')
    
    def on_closing(self):
        """Cierra aplicación"""
        if messagebox.askokcancel("Salir", "¿Cerrar DocAssist?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RAGAssistantApp(root)
    root.mainloop()