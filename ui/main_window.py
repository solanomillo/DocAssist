"""
Ventana principal de la aplicación DocAssist - Versión mejorada
Contiene barra de progreso, tema moderno y mejor feedback visual
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sv_ttk  # Tema moderno
from ui.settings_dialog import SettingsDialog
from config.settings import ConfigManager
from core.rag_engine import RAGEngine
import os
import threading


class RAGAssistantApp:
    """
    Clase principal de la interfaz gráfica - Versión con feedback visual mejorado
    """
    
    def __init__(self, root):
        """
        Inicializa la ventana principal con tema moderno
        """
        self.root = root
        self.root.title("DocAssist - Asistente de Documentos")
        self.root.geometry("1000x650")  # Ligeramente más grande
        
        # Aplicar tema moderno (oscuro)
        sv_ttk.set_theme("dark")
        
        # Inicializar gestor de configuración
        self.config_manager = ConfigManager()
        
        # Variables
        self.api_provider = None
        self.api_key = None
        self.api_model = None
        self.rag_engine = None
        self.is_processing = False
        
        # Configurar grid principal
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
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
        
        main_frame.grid_rowconfigure(1, weight=1)  # Fila del contenido
        main_frame.grid_rowconfigure(0, weight=0)  # Fila de la barra de progreso
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # --- BARRA DE PROGRESO (inicialmente oculta) ---
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky='ew')
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=100
        )
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="Procesando...",
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
        """Añade mensaje al chat con formato mejorado"""
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
        
        timestamp = ""
        if tag != 'thinking':
            from datetime import datetime
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
        self.progress_frame.grid()
        self.progress_bar.start(10)
        self.root.update()
    
    def hide_progress(self):
        """Oculta la barra de progreso"""
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
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
            self.create_rag_engine()
            self.provider_status.config(text=f"⚙️ {self.api_provider} - {self.api_model}")
            self.add_to_chat("Sistema", f"⚙️ Configuración cargada: {self.api_provider} - {self.api_model}", 'success')
    
    def create_rag_engine(self):
        """Crea el motor RAG - VERSIÓN CORREGIDA (SIN barra de progreso)"""
        try:
            # Mostrar en consola solamente
            print(f"🔧 Inicializando RAGEngine: {self.api_provider} - {self.api_model}")
            
            self.rag_engine = RAGEngine(
                provider=self.api_provider,
                api_key=self.api_key,
                model=self.api_model
            )
            
            # Actualizar UI
            self.update_status(f"✅ Listo - {self.api_provider}")
            self.add_to_chat("Sistema", "🤖 Motor RAG inicializado correctamente", 'info')
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            self.update_status(f"❌ Error: {error_msg[:50]}...", True)
            self.add_to_chat("Sistema", f"❌ Error: {error_msg}", 'error')
            self.rag_engine = None
    
    def open_settings(self):
        """Abre el diálogo de configuración de API - VERSIÓN CORREGIDA"""
        # Crear y mostrar el diálogo
        dialog = SettingsDialog(self.root)
        
        # Esperar a que se cierre el diálogo
        self.root.wait_window(dialog)
        
        # Procesar el resultado
        if dialog.result:
            # Guardar la configuración
            self.api_provider = dialog.result['provider']
            self.api_key = dialog.result['api_key']
            self.api_model = dialog.result['model']
            
            # Guardar en .env (SIN barra de progreso)
            try:
                self.config_manager.save_api_config(
                    provider=self.api_provider,
                    api_key=self.api_key,
                    model=self.api_model
                )
            except Exception as e:
                print(f"Error guardando configuración: {e}")
            
            # Crear motor RAG (SIN barra de progreso)
            self.create_rag_engine()
            
            # Actualizar UI
            self.provider_status.config(text=f"⚙️ {self.api_provider} - {self.api_model}")
            self.add_to_chat("Sistema", 
                f"✅ API configurada: {self.api_provider} - {self.api_model}", 'success')
        else:
            self.add_to_chat("Sistema", "ℹ️ Configuración cancelada")
    def load_documents(self):
        """Manejador para cargar documentos - VERSIÓN SIMPLIFICADA SIN HILOS"""
        if not self.rag_engine:
            messagebox.showinfo("Info", "Configura una API primero")
            return
        
        files = filedialog.askopenfilenames(
            title="Seleccionar documentos",
            filetypes=[("Documentos", "*.pdf *.txt"), ("PDF", "*.pdf"), ("Texto", "*.txt")]
        )
        
        if not files:
            return
        
        # Deshabilitar botón
        self.load_btn.config(state='disabled')
        self.update_status("Procesando documentos...")
        
        # Forzar actualización de la UI
        self.root.update()
        
        try:
            # Procesar directamente (sin hilo)
            print(f"📂 Procesando {len(files)} archivo(s)...")
            success = self.rag_engine.load_documents(list(files))
            
            if success:
                # Actualizar lista
                self.docs_listbox.delete(0, tk.END)
                for f in files:
                    self.docs_listbox.insert(tk.END, f"📄 {os.path.basename(f)}")
                
                self.ask_btn.config(state='normal')
                self.update_status(f"✅ {len(files)} documento(s) cargado(s)")
                self.add_to_chat("Sistema", f"✅ {len(files)} documento(s) cargado(s)", 'success')
            else:
                self.update_status("❌ Error al cargar documentos", True)
                self.add_to_chat("Sistema", "❌ Error al cargar documentos", 'error')
                
        except Exception as e:
            self.update_status("❌ Error", True)
            self.add_to_chat("Sistema", f"❌ Error: {str(e)}", 'error')
            print(f"❌ Error detallado: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Rehabilitar botón
            self.load_btn.config(state='normal')
            self.root.update()
    
    def _on_documents_loaded(self, success, files):
        """Callback cuando se cargan documentos"""
        self.hide_progress()
        self.load_btn.config(state='normal')
        
        if success:
            self.docs_listbox.delete(0, tk.END)
            for f in files:
                self.docs_listbox.insert(tk.END, f"📄 {os.path.basename(f)}")
            
            self.ask_btn.config(state='normal')
            self.update_status(f"✅ {len(files)} documento(s) cargado(s)")
            self.add_to_chat("Sistema", f"✅ {len(files)} documento(s) cargado(s)", 'success')
        else:
            self.update_status("❌ Error al cargar documentos", True)
            self.add_to_chat("Sistema", "❌ Error al cargar documentos", 'error')
    
    def _on_documents_error(self, error):
        """Callback cuando hay error"""
        self.hide_progress()
        self.load_btn.config(state='normal')
        self.update_status("❌ Error", True)
        self.add_to_chat("Sistema", f"❌ Error: {str(error)}", 'error')
    
    def ask_question(self):
        """Hace pregunta - VERSIÓN SIMPLIFICADA SIN HILOS"""
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
        self.root.update()
        
        try:
            # Procesar directamente (sin hilo)
            print(f"❓ Pregunta: {question}")
            response = self.rag_engine.ask(question)
            
            # Mostrar respuesta
            self.add_to_chat("Asistente", response)
            self.update_status("✅ Listo")
            
        except Exception as e:
            self.update_status("❌ Error", True)
            self.add_to_chat("Sistema", f"❌ Error: {str(e)}", 'error')
            print(f"❌ Error detallado: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Rehabilitar controles
            self.is_processing = False
            self.ask_btn.config(state='normal')
            self.question_entry.config(state='normal')
            self.question_entry.focus()
            self.root.update()
    
    def _on_answer_received(self, response, thinking_id):
        """Callback cuando llega la respuesta"""
        # Eliminar mensaje de pensando y mostrar respuesta
        self.remove_last_message()
        self.add_to_chat("Asistente", response)
        
        # Rehabilitar controles
        self.is_processing = False
        self.ask_btn.config(state='normal')
        self.question_entry.config(state='normal')
        self.question_entry.focus()
        self.update_status("✅ Listo")
    
    def _on_answer_error(self, error, thinking_id):
        """Callback cuando hay error"""
        self.remove_last_message()
        self.add_to_chat("Sistema", f"❌ Error: {str(error)}", 'error')
        
        self.is_processing = False
        self.ask_btn.config(state='normal')
        self.question_entry.config(state='normal')
        self.update_status("❌ Error", True)
    
    def remove_last_message(self):
        """Elimina último mensaje"""
        self.chat_display.config(state='normal')
        content = self.chat_display.get("1.0", tk.END)
        messages = content.split("\n\n")
        if len(messages) > 2:
            new_content = "\n\n".join(messages[:-2]) + "\n\n"
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.insert("1.0", new_content)
        self.chat_display.config(state='disabled')
    
    def clear_configuration(self):
        """Limpia configuración"""
        if messagebox.askyesno("Confirmar", "¿Eliminar configuración?"):
            self.api_provider = None
            self.api_key = None
            self.api_model = None
            self.rag_engine = None
            self.config_manager.clear_api_config()
            self.provider_status.config(text="⚙️ Sin configurar")
            self.add_to_chat("Sistema", "🗑️ Configuración eliminada", 'system')
    
    def clear_vectorstore(self):
        """Limpia base de datos vectorial"""
        if self.rag_engine and messagebox.askyesno("Confirmar", "¿Eliminar base de datos?"):
            self.rag_engine.clear_vectorstore()
            self.docs_listbox.delete(0, tk.END)
            self.ask_btn.config(state='disabled')
            self.add_to_chat("Sistema", "🧹 Base de datos eliminada", 'info')
    
    def on_closing(self):
        """Cierra aplicación"""
        if messagebox.askokcancel("Salir", "¿Cerrar DocAssist?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RAGAssistantApp(root)
    root.mainloop()