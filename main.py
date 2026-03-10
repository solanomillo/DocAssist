"""
DocAssist - Asistente de Documentación Inteligente
Punto de entrada principal de la aplicación
"""

import tkinter as tk
from ui.main_window import RAGAssistantApp  # IMPORTAR desde ui.main_window


def main():
    """
    Función principal que inicia la aplicación
    """
    print("🚀 Iniciando DocAssist v0.5...")
    root = tk.Tk()
    
    # Crear y configurar la aplicación usando la clase IMPORTADA
    app = RAGAssistantApp(root)
    
    # Iniciar el bucle principal
    root.mainloop()


if __name__ == "__main__":
    main()