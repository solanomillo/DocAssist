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
    print("=" * 50)
    print("🚀 Iniciando DocAssist v0.7...")
    print("=" * 50)
    
    try:
        root = tk.Tk()
        app = RAGAssistantApp(root)
        root.mainloop()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        input("Presiona Enter para salir...")


if __name__ == "__main__":
    main()