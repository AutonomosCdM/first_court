"""Configuración del sistema."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_DIR = BASE_DIR / 'credentials'
TEMP_DIR = BASE_DIR / 'temp'

# Credenciales de Google
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', str(CREDENTIALS_DIR / 'google_credentials.json'))
GOOGLE_TOKEN_FILE = os.getenv('GOOGLE_TOKEN_FILE', str(CREDENTIALS_DIR / 'google_token.json'))

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_SSL = os.getenv('REDIS_SSL', '0').lower() in ('true', '1', 't')

# Configuración de WebSocket
WS_HEARTBEAT_INTERVAL = int(os.getenv('WS_HEARTBEAT_INTERVAL', '30'))  # segundos
WS_MESSAGE_QUEUE_SIZE = int(os.getenv('WS_MESSAGE_QUEUE_SIZE', '100'))

# S3
S3_BUCKET = os.getenv('S3_BUCKET', 'first-court-dev')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Configuración de pruebas
TEST_GOOGLE_CREDENTIALS_FILE = os.getenv('TEST_GOOGLE_CREDENTIALS_FILE', str(CREDENTIALS_DIR / 'test_google_credentials.json'))
TEST_GOOGLE_TOKEN_FILE = os.getenv('TEST_GOOGLE_TOKEN_FILE', str(CREDENTIALS_DIR / 'test_google_token.json'))
TEST_DRIVE_ROOT_FOLDER = os.getenv('TEST_DRIVE_ROOT_FOLDER')  # ID de la carpeta de pruebas en Drive

# Elasticsearch
ES_URL = os.getenv('ES_URL', 'http://localhost:9200')
ES_USER = os.getenv('ES_USER', '')
ES_PASSWORD = os.getenv('ES_PASSWORD', '')
ES_VERIFY_CERTS = os.getenv('ES_VERIFY_CERTS', '1').lower() in ('true', '1', 't')

# Asegurar que existan los directorios necesarios
CREDENTIALS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
