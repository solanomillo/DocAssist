"""
DocAssist - Asistente de Documentación Inteligente
Punto de entrada principal de la aplicación
"""

import tkinter as tk
from tkinter import ttk


class DocAssistApp:
    """
    Clase principal de la aplicación
    Versión inicial: solo ventana básica con título y label centrado
    """
    
    def __init__(self, root):
        """
        Inicializa la ventana principal
        
        Args:
            root: Ventana raíz de Tkinter
        """
        self.root = root
        self.root.title("DocAssist - Asistente de Documentos")
        self.root.geometry("900x600")
        
        # Configurar color de fondo modo oscuro
        self.root.configure(bg='#2b2b2b')
        
        # Centrar la ventana en la pantalla
        self.center_window()
        
        # Crear un frame contenedor para centrar el contenido
        main_frame = tk.Frame(root, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both')
        
        # Label de bienvenida centrado
        welcome_label = tk.Label(
            main_frame,
            text="DocAssist v0.1 - Cargando...",
            font=("Arial", 16),
            fg='#ffffff',
            bg='#2b2b2b'
        )
        welcome_label.pack(expand=True)
        
        # Vincular evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """
        Centra la ventana en la pantalla
        """
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_closing(self):
        """
        Maneja el evento de cierre de la ventana
        """
        print("Cerrando DocAssist...")
        self.root.destroy()


def main():
    """
    Función principal que inicia la aplicación
    """
    print("Iniciando DocAssist v0.1...")
    root = tk.Tk()
    app = DocAssistApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()