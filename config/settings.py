"""
Módulo de configuración para DocAssist
Gestiona la persistencia de API keys y configuración usando archivo .env
"""

import os
import sys
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
    API_PLAN_KEY = "DOCASSIST_API_PLAN"
    
    def __init__(self):
        """
        Inicializa el gestor de configuración
        Busca el .env en la carpeta del ejecutable o en la raíz del proyecto
        """
        # Determinar la carpeta base (donde está el .exe o el script)
        if getattr(sys, 'frozen', False):
            # Estamos en un ejecutable PyInstaller
            self.root_dir = Path(sys.executable).parent
        else:
            # Estamos en desarrollo
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
            print(f"📝 Archivo .env no encontrado en {self.env_path}. Se creará al guardar configuración.")
    
    def save_api_config(self, provider, api_key, model, plan="free"):
        """
        Guarda la configuración de API en el archivo .env
        
        Args:
            provider (str): Nombre del proveedor
            api_key (str): API key (puede estar vacía para Ollama)
            model (str): Modelo seleccionado
            plan (str): 'free' o 'paid'
        
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            # Asegurar que el directorio existe
            self.root_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar cada variable en el archivo .env
            set_key(self.env_path, self.API_PROVIDER_KEY, provider)
            set_key(self.env_path, self.API_KEY_KEY, api_key if api_key else "")
            set_key(self.env_path, self.API_MODEL_KEY, model)
            set_key(self.env_path, self.API_PLAN_KEY, plan)
            
            print(f"✅ Configuración guardada en: {self.env_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar configuración: {e}")
            return False
    
    def load_api_config(self):
        """
        Carga la configuración de API desde el archivo .env
        
        Returns:
            dict: Diccionario con provider, api_key, model, plan o None si no existe
        """
        if not self.env_path.exists():
            print(f"ℹ️ No existe archivo .env en {self.env_path}")
            return None
        
        # Recargar variables por si acaso
        load_dotenv(self.env_path, override=True)
        
        provider = os.getenv(self.API_PROVIDER_KEY)
        api_key = os.getenv(self.API_KEY_KEY)
        model = os.getenv(self.API_MODEL_KEY)
        plan = os.getenv(self.API_PLAN_KEY, "free")
        
        # Verificar que tenemos todos los datos necesarios
        if provider and model:
            config = {
                'provider': provider,
                'api_key': api_key if api_key else "",
                'model': model,
                'plan': plan
            }
            print(f"✅ Configuración cargada: {provider} - {model} ({plan})")
            return config
        else:
            print(f"ℹ️ No se encontró configuración completa en {self.env_path}")
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
                            self.API_MODEL_KEY,
                            self.API_PLAN_KEY
                        ]):
                            f.write(line)
                
                print(f"✅ Configuración eliminada del archivo .env")
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