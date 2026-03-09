"""
DocAssist - Asistente de Documentación Inteligente
Punto de entrada principal de la aplicación
"""

import tkinter as tk
from ui.main_window import RAGAssistantApp


def main():
    """
    Función principal que inicia la aplicación
    """
    print("🚀 Iniciando DocAssist v0.2...")
    root = tk.Tk()
    
    # Crear y configurar la aplicación
    app = RAGAssistantApp(root)
    
    # Iniciar el bucle principal
    root.mainloop()


if __name__ == "__main__":
    main()