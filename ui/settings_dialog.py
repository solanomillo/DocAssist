"""
Diálogo de configuración de API para DocAssist
Permite seleccionar proveedor, tipo de plan, API key y modelo
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
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        # Variables
        self.provider_var = tk.StringVar(value="Google Gemini")  # Default a Gemini
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.plan_var = tk.StringVar(value="free")  # 'free' o 'paid'
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
        
        # --- TÍTULO INFORMATIVO ---
        title_label = ttk.Label(
            main_frame, 
            text="Configuración de API para IA",
            font=('Arial', 12, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # --- PROVEEDOR ---
        ttk.Label(main_frame, text="Proveedor:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=(0, 10)
        )
        
        # Frame para radiobuttons
        provider_frame = ttk.Frame(main_frame)
        provider_frame.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
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
            text="Ollama (Local)",
            variable=self.provider_var,
            value="Ollama",
            command=self.on_provider_change
        ).grid(row=1, column=1, padx=(0, 15), sticky='w', pady=(5, 0))
        
        # --- API KEY ---
        ttk.Label(main_frame, text="API Key:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=(10, 10)
        )
        
        self.api_key_entry = ttk.Entry(
            main_frame,
            textvariable=self.api_key_var,
            show="•",
            width=50
        )
        self.api_key_entry.grid(row=2, column=1, sticky='ew', pady=(10, 10), padx=(0, 10))
        
        # Nota para Ollama
        self.ollama_note = ttk.Label(
            main_frame,
            text="📌 Ollama es local y gratuito - no requiere API key",
            foreground='#4CAF50',
            font=('Arial', 9, 'italic')
        )
        self.ollama_note.grid(row=3, column=0, columnspan=2, sticky='w', pady=(0, 10))
        self.ollama_note.grid_remove()
        
        # --- MODELO ---
        ttk.Label(main_frame, text="Modelo:", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky='w', pady=(0, 10)
        )
        
        self.model_combo = ttk.Combobox(
            main_frame,
            textvariable=self.model_var,
            state='readonly',
            width=47
        )
        self.model_combo.grid(row=4, column=1, sticky='w', pady=(0, 10))
        
        # --- TIPO DE PLAN ---
        ttk.Label(main_frame, text="Tipo de Plan:", font=('Arial', 10, 'bold')).grid(
            row=5, column=0, sticky='w', pady=(10, 10)
        )
        
        plan_frame = ttk.Frame(main_frame)
        plan_frame.grid(row=5, column=1, sticky='w', pady=(10, 10))
        
        ttk.Radiobutton(
            plan_frame,
            text="Gratuito (con límites)",
            variable=self.plan_var,
            value="free"
        ).pack(side='left', padx=(0, 15))
        
        ttk.Radiobutton(
            plan_frame,
            text="De Pago (límites altos)",
            variable=self.plan_var,
            value="paid"
        ).pack(side='left')
        
        # Nota informativa de planes
        self.plan_note = ttk.Label(
            main_frame,
            text="",
            foreground='#888888',
            font=('Arial', 9, 'italic'),
            wraplength=400
        )
        self.plan_note.grid(row=6, column=0, columnspan=2, sticky='w', pady=(0, 15))
        self.update_plan_note()
        
        # --- BOTONES ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
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
        self.update_plan_note()
        
        if provider == "Ollama":
            self.api_key_var.set("")
            self.api_key_entry.config(state='disabled')
            # Ollama siempre es "gratis" pero sin límites
            self.plan_var.set("free")
        else:
            self.api_key_entry.config(state='normal')
    
    def update_ollama_note(self):
        """Muestra/oculta nota de Ollama"""
        if self.provider_var.get() == "Ollama":
            self.ollama_note.grid()
        else:
            self.ollama_note.grid_remove()
    
    def update_plan_note(self):
        """Actualiza la nota según el proveedor y plan"""
        provider = self.provider_var.get()
        plan = self.plan_var.get()
        
        if provider == "Ollama":
            note = "✅ Ollama es completamente local y gratuito. Sin límites de API."
            self.plan_note.config(foreground='#4CAF50')
        elif provider == "Google Gemini":
            if plan == "free":
                note = "📊 Plan Gratuito Gemini: 100 solicitudes/minuto para embeddings. Recomendado para pruebas."
            else:
                note = "⚡ Plan de Pago Gemini: Límites mucho más altos (1500+ solicitudes/minuto)."
            self.plan_note.config(foreground='#888888')
        elif provider == "OpenAI":
            if plan == "free":
                note = "📊 OpenAI Gratuito: Créditos iniciales. Límites variables por endpoint."
            else:
                note = "⚡ OpenAI de Pago: Pago por uso. Límites según tu configuración."
            self.plan_note.config(foreground='#888888')
        elif provider == "Anthropic":
            if plan == "free":
                note = "📊 Anthropic Gratuito: Créditos iniciales limitados."
            else:
                note = "⚡ Anthropic de Pago: Pago por uso. Límites más altos."
            self.plan_note.config(foreground='#888888')
        
        self.plan_note.config(text=note)
    
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
            'model': self.model_var.get(),
            'plan': self.plan_var.get()
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