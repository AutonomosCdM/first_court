"""Configuración para pruebas."""
import os
from pathlib import Path

# Paths
TEST_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = TEST_DIR / 'credentials'
TEMP_DIR = TEST_DIR / 'temp'

# Credenciales de Google
TEST_GOOGLE_CREDENTIALS_FILE = str(CREDENTIALS_DIR / 'test_google_credentials.json')
TEST_GOOGLE_TOKEN = os.getenv('TEST_GOOGLE_TOKEN')
TEST_DRIVE_ROOT_FOLDER = os.getenv('TEST_DRIVE_ROOT_FOLDER')

# Verificar credenciales
if not os.path.exists(TEST_GOOGLE_CREDENTIALS_FILE):
    raise Exception('TEST_GOOGLE_CREDENTIALS_FILE no encontrado')
if not TEST_GOOGLE_TOKEN:
    raise Exception('TEST_GOOGLE_TOKEN no configurado')
if not TEST_DRIVE_ROOT_FOLDER:
    raise Exception('TEST_DRIVE_ROOT_FOLDER no configurado')

# Guardar token
with open(str(CREDENTIALS_DIR / 'test_google_token.json'), 'w') as f:
    f.write(TEST_GOOGLE_TOKEN)

# Asegurar que existan los directorios necesarios
CREDENTIALS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Configuración de pruebas
TEST_USERS = {
    'juez': 'test.juez@autonomos.dev',
    'fiscal': 'test.fiscal@autonomos.dev',
    'defensor': 'test.defensor@autonomos.dev'
}
