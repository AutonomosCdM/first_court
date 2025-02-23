import os
from dotenv import load_dotenv

load_dotenv()

from src.court.court_agent import CourtAgent
from src.agents.judge import JudgeAgent
from src.agents.prosecutor import ProsecutorAgent
from src.agents.defender import DefenderAgent
from src.agents.secretary import SecretaryAgent

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Cargar credenciales de Google desde los secretos de GitHub
creds = Credentials(
    token=os.getenv('GOOGLE_TOKEN'),
    refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
)

# Crear el servicio de Google Drive
drive_service = build('drive', 'v3', credentials=creds)

# Actualizar la carpeta de Google Drive a utilizar
GOOGLE_DRIVE_FOLDER_ID = '1fagq1gTX0E0v0g9AZ2e245t0vg8T3YIk'

court_agent = CourtAgent(drive_service, GOOGLE_DRIVE_FOLDER_ID)
court_agent.handle_case({
    'id': 'CASO-2025-002',
    'tipo_analisis': 'general',
    'imputado': 'Claudio Rosamel Lavado Castro',
    'hechos': 'Los querellados ofrecieron a los estudiantes una carrera técnica de Hotelería y Turismo que no estaba acreditada.'
})
