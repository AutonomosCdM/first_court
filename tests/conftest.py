"""Configuración global de pytest."""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

def pytest_configure(config):
    """Configurar variables de entorno para pruebas."""
    # Cargar variables de entorno de prueba
    env_file = Path(__file__).parent.parent / '.env.test'
    if env_file.exists():
        load_dotenv(env_file)
    
    # Configurar variables de entorno por defecto si no existen
    if not os.getenv('TEST_DRIVE_ROOT_FOLDER'):
        pytest.skip('TEST_DRIVE_ROOT_FOLDER no configurado. Crea una carpeta en Drive y configura su ID.')
    
    # Verificar credenciales
    if not os.getenv('TEST_DRIVE_ROOT_FOLDER'):
        pytest.skip('TEST_DRIVE_ROOT_FOLDER no configurado')
