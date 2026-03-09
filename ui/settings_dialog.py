"""
Diálogo de configuración de API para DocAssist
Permite seleccionar proveedor, ingresar API key y elegir modelo
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsDialog(tk.Toplevel):
    """
    Diálogo modal para configurar la API de IA
    Hereda de Toplevel para crear una ventana independiente pero modal
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
        
        Args:
            parent: Ventana padre (main_window)
        """
        super().__init__(parent)
        
        # Configuración de la ventana
        self.title("⚙️ Configurar API")
        self.geometry("450x350")
        self.resizable(False, False)
        
        # Hacer la ventana modal
        self.transient(parent)  # Establece relación con la ventana padre
        self.grab_set()  # Captura todos los eventos
        
        # Variables para almacenar los valores
        self.provider_var = tk.StringVar(value="OpenAI")  # Valor por defecto
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar()
        
        # Resultado (se establecerá cuando se guarde)
        self.result = None
        
        # Configurar el grid
        self.configure_grid()
        
        # Crear los widgets
        self.create_widgets()
        
        # Inicializar modelos según proveedor por defecto
        self.update_models_list()
        
        # Centrar la ventana respecto al padre
        self.center_window()
        
        # Vincular tecla Escape para cerrar
        self.bind('<Escape>', lambda e: self.cancel())
        
        # Esperar a que se cierre la ventana
        self.wait_window()
    
    def configure_grid(self):
        """Configura las columnas del grid para alineación"""
        self.grid_columnconfigure(0, weight=0)  # Etiquetas
        self.grid_columnconfigure(1, weight=1)  # Campos de entrada
    
    def create_widgets(self):
        """Crea todos los widgets del diálogo"""
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configurar grid del main_frame
        main_frame.grid_columnconfigure(1, weight=1)
        
        # --- PROVEEDOR ---
        ttk.Label(main_frame, text="Proveedor:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=(0, 10)
        )
        
        # Frame para los radiobuttons
        provider_frame = ttk.Frame(main_frame)
        provider_frame.grid(row=0, column=1, sticky='w', pady=(0, 10))
        
        # Crear radiobuttons para cada proveedor
        providers = list(self.PROVIDER_MODELS.keys())
        for i, provider in enumerate(providers):
            rb = ttk.Radiobutton(
                provider_frame,
                text=provider,
                variable=self.provider_var,
                value=provider,
                command=self.on_provider_change
            )
            rb.grid(row=0, column=i, padx=(0, 15))
        
        # --- API KEY ---
        ttk.Label(main_frame, text="API Key:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=(0, 10)
        )
        
        # Entry para API key (con ocultación de caracteres)
        self.api_key_entry = ttk.Entry(
            main_frame,
            textvariable=self.api_key_var,
            show="•",  # Oculta los caracteres
            width=40
        )
        self.api_key_entry.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Nota para Ollama (no requiere API key)
        self.ollama_note = ttk.Label(
            main_frame,
            text="📌 Nota: Ollama no requiere API key (ejecuta modelos localmente)",
            foreground='#666666',
            font=('Arial', 9, 'italic')
        )
        self.ollama_note.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # --- MODELO ---
        ttk.Label(main_frame, text="Modelo:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky='w', pady=(0, 20)
        )
        
        # Combobox para seleccionar modelo
        self.model_combo = ttk.Combobox(
            main_frame,
            textvariable=self.model_var,
            state='readonly',
            width=38
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
        
        # Configurar estado inicial de la nota de Ollama
        self.update_ollama_note()
    
    def on_provider_change(self):
        """
        Se ejecuta cuando cambia el proveedor seleccionado
        Actualiza la lista de modelos y el estado del campo API key
        """
        provider = self.provider_var.get()
        self.update_models_list()
        self.update_ollama_note()
        
        # Si es Ollama, limpiar y deshabilitar API key
        if provider == "Ollama":
            self.api_key_var.set("")  # Limpiar API key
            self.api_key_entry.config(state='disabled')
        else:
            self.api_key_entry.config(state='normal')
    
    def update_ollama_note(self):
        """Muestra/oculta la nota sobre Ollama según el proveedor"""
        if self.provider_var.get() == "Ollama":
            self.ollama_note.grid()
        else:
            self.ollama_note.grid_remove()
    
    def update_models_list(self):
        """Actualiza la lista de modelos según el proveedor seleccionado"""
        provider = self.provider_var.get()
        models = self.PROVIDER_MODELS.get(provider, [])
        
        self.model_combo['values'] = models
        
        # Seleccionar el primer modelo por defecto
        if models:
            self.model_var.set(models[0])
    
    def validate_inputs(self):
        """
        Valida que los campos requeridos estén completos
        
        Returns:
            bool: True si la validación pasa, False en caso contrario
        """
        provider = self.provider_var.get()
        
        # Validar API key (excepto para Ollama)
        if provider != "Ollama":
            api_key = self.api_key_var.get().strip()
            if not api_key:
                messagebox.showerror(
                    "Error de validación",
                    f"API Key es requerida para {provider}.\n\n"
                    "Puedes obtener tu API key en:\n"
                    f"• OpenAI: https://platform.openai.com/api-keys\n"
                    f"• Anthropic: https://console.anthropic.com/\n"
                    f"• Google Gemini: https://makersuite.google.com/app/apikey"
                )
                return False
            
            # Validación básica de formato (opcional)
            if len(api_key) < 20:
                if not messagebox.askyesno(
                    "Advertencia",
                    "La API key ingresada es muy corta. ¿Estás seguro de que es correcta?"
                ):
                    return False
        
        # Validar que se haya seleccionado un modelo
        if not self.model_var.get():
            messagebox.showerror(
                "Error de validación",
                "Por favor, selecciona un modelo."
            )
            return False
        
        return True
    
    def save_settings(self):
        """Guarda la configuración y cierra el diálogo"""
        if not self.validate_inputs():
            return
        
        # Guardar los valores en el resultado
        self.result = {
            'provider': self.provider_var.get(),
            'api_key': self.api_key_var.get().strip(),
            'model': self.model_var.get()
        }
        
        # Cerrar el diálogo
        self.destroy()
    
    def cancel(self):
        """Cancela la configuración y cierra el diálogo"""
        self.result = None
        self.destroy()
    
    def center_window(self):
        """Centra la ventana respecto a la ventana padre"""
        self.update_idletasks()
        
        # Obtener dimensiones de la ventana padre
        parent = self.master
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calcular posición centrada
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')


# Función para pruebas independientes
def test_dialog():
    """Función para probar el diálogo directamente"""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    dialog = SettingsDialog(root)
    
    if dialog.result:
        print("✅ Configuración guardada:")
        print(f"  Proveedor: {dialog.result['provider']}")
        print(f"  API Key: {'*' * len(dialog.result['api_key'])}")
        print(f"  Modelo: {dialog.result['model']}")
    else:
        print("❌ Configuración cancelada")
    
    root.destroy()


if __name__ == "__main__":
    test_dialog()