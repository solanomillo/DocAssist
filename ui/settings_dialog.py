"""
Diálogo de configuración de API para DocAssist
Permite seleccionar proveedor, ingresar API key y elegir modelo
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsDialog(tk.Toplevel):
    """
    Diálogo modal para configurar la API de IA
    """
    
    # Diccionario con los modelos sugeridos por proveedor
    PROVIDER_MODELS = {
        "OpenAI": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4.1",
            "gpt-4.1-mini"
        ],
        
        "Anthropic": [
            "claude-3-opus",
            "claude-3.5-sonnet",
            "claude-3-haiku"
        ],
        
        "Google Gemini": [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-1.5-pro"
        ],
        
        "Ollama": [
            "llama3",
            "mistral",
            "phi3",
            "codellama"
        ]
    }
    
    def __init__(self, parent):
        """
        Inicializa el diálogo de configuración
        """
        super().__init__(parent)
        
        # Configuración de la ventana
        self.title("⚙️ Configurar API")
        self.geometry("550x380")
        self.resizable(False, False)
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        # Variables
        self.provider_var = tk.StringVar(value="OpenAI")
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.result = None
        
        # Crear widgets
        self.create_widgets()
        
        # Inicializar modelos
        self.update_models_list()
        
        # Centrar ventana
        self.center_window()
        
        # Vincular tecla Escape
        self.bind('<Escape>', lambda e: self.cancel())
        self.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def create_widgets(self):
        """Crea todos los widgets del diálogo"""
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configurar grid
        main_frame.grid_columnconfigure(1, weight=1)
        
        # --- PROVEEDOR ---
        ttk.Label(main_frame, text="Proveedor:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=(0, 10)
        )
        
        # Frame para radiobuttons
        provider_frame = ttk.Frame(main_frame)
        provider_frame.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Primera fila: OpenAI, Anthropic
        ttk.Radiobutton(
            provider_frame,
            text="OpenAI",
            variable=self.provider_var,
            value="OpenAI",
            command=self.on_provider_change
        ).grid(row=0, column=0, padx=(0, 15), sticky='w')
        
        ttk.Radiobutton(
            provider_frame,
            text="Anthropic",
            variable=self.provider_var,
            value="Anthropic",
            command=self.on_provider_change
        ).grid(row=0, column=1, padx=(0, 15), sticky='w')
        
        # Segunda fila: Google Gemini, Ollama
        ttk.Radiobutton(
            provider_frame,
            text="Google Gemini",
            variable=self.provider_var,
            value="Google Gemini",
            command=self.on_provider_change
        ).grid(row=1, column=0, padx=(0, 15), sticky='w', pady=(5, 0))
        
        ttk.Radiobutton(
            provider_frame,
            text="Ollama",
            variable=self.provider_var,
            value="Ollama",
            command=self.on_provider_change
        ).grid(row=1, column=1, padx=(0, 15), sticky='w', pady=(5, 0))
        
        # --- API KEY ---
        ttk.Label(main_frame, text="API Key:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=(10, 10)
        )
        
        self.api_key_entry = ttk.Entry(
            main_frame,
            textvariable=self.api_key_var,
            show="•",
            width=50
        )
        self.api_key_entry.grid(row=1, column=1, sticky='ew', pady=(10, 10), padx=(0, 10))
        
        # Nota para Ollama
        self.ollama_note = ttk.Label(
            main_frame,
            text="📌 Ollama no requiere API key (modelos locales gratuitos)",
            foreground='#888888',
            font=('Arial', 9, 'italic')
        )
        self.ollama_note.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 10))
        self.ollama_note.grid_remove()
        
        # --- MODELO ---
        ttk.Label(main_frame, text="Modelo:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky='w', pady=(0, 20)
        )
        
        self.model_combo = ttk.Combobox(
            main_frame,
            textvariable=self.model_var,
            state='readonly',
            width=47
        )
        self.model_combo.grid(row=3, column=1, sticky='w', pady=(0, 20))
        
        # --- BOTONES ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Guardar",
            command=self.save_settings,
            width=15
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.cancel,
            width=15
        ).pack(side='left', padx=5)
    
    def on_provider_change(self):
        """Maneja cambio de proveedor"""
        provider = self.provider_var.get()
        self.update_models_list()
        self.update_ollama_note()
        
        if provider == "Ollama":
            self.api_key_var.set("")
            self.api_key_entry.config(state='disabled')
        else:
            self.api_key_entry.config(state='normal')
    
    def update_ollama_note(self):
        """Muestra/oculta nota de Ollama"""
        if self.provider_var.get() == "Ollama":
            self.ollama_note.grid()
        else:
            self.ollama_note.grid_remove()
    
    def update_models_list(self):
        """Actualiza lista de modelos"""
        provider = self.provider_var.get()
        models = self.PROVIDER_MODELS.get(provider, [])
        self.model_combo['values'] = models
        if models:
            self.model_var.set(models[0])
    
    def validate_inputs(self):
        """Valida inputs"""
        provider = self.provider_var.get()
        
        if provider != "Ollama":
            api_key = self.api_key_var.get().strip()
            if not api_key:
                messagebox.showerror(
                    "Error de validación",
                    f"API Key es requerida para {provider}"
                )
                return False
        
        if not self.model_var.get():
            messagebox.showerror(
                "Error de validación",
                "Por favor, selecciona un modelo."
            )
            return False
        
        return True
    
    def save_settings(self):
        """Guarda configuración"""
        if not self.validate_inputs():
            return
        
        self.result = {
            'provider': self.provider_var.get(),
            'api_key': self.api_key_var.get().strip(),
            'model': self.model_var.get()
        }
        self.destroy()
    
    def cancel(self):
        """Cancela"""
        self.result = None
        self.destroy()
    
    def center_window(self):
        """Centra ventana"""
        self.update_idletasks()
        parent = self.master
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    dialog = SettingsDialog(root)
    root.wait_window(dialog)
    if dialog.result:
        print("Configuración guardada:", dialog.result)
    root.destroy()