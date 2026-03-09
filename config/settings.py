"""
Módulo de configuración para DocAssist
Gestiona la persistencia de API keys y configuración usando archivo .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv, set_key


class ConfigManager:
    """
    Gestor de configuración persistente para DocAssist
    Maneja la lectura/escritura de API keys y preferencias en archivo .env
    """
    
    # Constantes para las claves del archivo .env
    API_PROVIDER_KEY = "DOCASSIST_API_PROVIDER"
    API_KEY_KEY = "DOCASSIST_API_KEY"
    API_MODEL_KEY = "DOCASSIST_API_MODEL"
    
    def __init__(self):
        """
        Inicializa el gestor de configuración
        Define la ruta al archivo .env en la raíz del proyecto
        """
        # Obtener la ruta raíz del proyecto (donde está main.py)
        self.root_dir = Path(__file__).parent.parent
        self.env_path = self.root_dir / '.env'
        
        # Cargar variables de entorno existentes
        self.load_env_file()
    
    def load_env_file(self):
        """
        Carga el archivo .env si existe
        """
        if self.env_path.exists():
            load_dotenv(self.env_path)
            print(f"✅ Archivo .env cargado desde: {self.env_path}")
        else:
            print(f"📝 Archivo .env no encontrado. Se creará al guardar configuración.")
    
    def save_api_config(self, provider, api_key, model):
        """
        Guarda la configuración de API en el archivo .env
        
        Args:
            provider (str): Nombre del proveedor (OpenAI, Anthropic, etc.)
            api_key (str): API key (puede estar vacía para Ollama)
            model (str): Modelo seleccionado
        
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Asegurar que el directorio existe
            self.root_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar cada variable en el archivo .env
            set_key(self.env_path, self.API_PROVIDER_KEY, provider)
            set_key(self.env_path, self.API_KEY_KEY, api_key if api_key else "")
            set_key(self.env_path, self.API_MODEL_KEY, model)
            
            print(f"✅ Configuración guardada en: {self.env_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar configuración: {e}")
            return False
    
    def load_api_config(self):
        """
        Carga la configuración de API desde el archivo .env
        
        Returns:
            dict: Diccionario con provider, api_key, model o None si no existe
        """
        if not self.env_path.exists():
            return None
        
        # Recargar variables por si acaso
        load_dotenv(self.env_path, override=True)
        
        provider = os.getenv(self.API_PROVIDER_KEY)
        api_key = os.getenv(self.API_KEY_KEY)
        model = os.getenv(self.API_MODEL_KEY)
        
        # Verificar que tenemos todos los datos necesarios
        if provider and model:
            config = {
                'provider': provider,
                'api_key': api_key if api_key else "",
                'model': model
            }
            print(f"✅ Configuración cargada: {provider} - {model}")
            return config
        else:
            print("ℹ️ No se encontró configuración completa en .env")
            return None
    
    def clear_api_config(self):
        """
        Elimina la configuración de API del archivo .env
        
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            if self.env_path.exists():
                # Leer todas las líneas excepto las de DocAssist
                with open(self.env_path, 'r') as f:
                    lines = f.readlines()
                
                # Filtrar líneas que no sean de DocAssist
                with open(self.env_path, 'w') as f:
                    for line in lines:
                        if not any(key in line for key in [
                            self.API_PROVIDER_KEY,
                            self.API_KEY_KEY,
                            self.API_MODEL_KEY
                        ]):
                            f.write(line)
                
                print("✅ Configuración eliminada del archivo .env")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error al eliminar configuración: {e}")
            return False
    
    def get_env_path(self):
        """
        Retorna la ruta al archivo .env
        
        Returns:
            Path: Ruta al archivo .env
        """
        return self.env_path


# Función de prueba
def test_config_manager():
    """Prueba el funcionamiento del ConfigManager"""
    print("🧪 Probando ConfigManager...")
    
    config_mgr = ConfigManager()
    
    # Probar guardado
    print("\n📝 Guardando configuración de prueba...")
    config_mgr.save_api_config(
        provider="OpenAI",
        api_key="sk-test123456789",
        model="gpt-3.5-turbo"
    )
    
    # Probar carga
    print("\n📖 Cargando configuración...")
    loaded = config_mgr.load_api_config()
    if loaded:
        print(f"   Proveedor: {loaded['provider']}")
        print(f"   API Key: {'*' * len(loaded['api_key'])}")
        print(f"   Modelo: {loaded['model']}")
    
    # Mostrar ruta del archivo
    print(f"\n📁 Archivo .env en: {config_mgr.get_env_path()}")
    
    # Probar limpieza
    print("\n🧹 Limpiando configuración...")
    config_mgr.clear_api_config()
    
    # Verificar que se eliminó
    loaded_after = config_mgr.load_api_config()
    print(f"   Configuración después de limpiar: {loaded_after}")
    
    print("\n✅ Prueba completada")


if __name__ == "__main__":
    test_config_manager()