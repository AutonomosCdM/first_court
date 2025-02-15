"""
Configuración de APIs de Google
"""

# Scopes requeridos para todas las funcionalidades
GOOGLE_API_SCOPES = [
    'https://www.googleapis.com/auth/calendar',              # Calendario y Meet
    'https://www.googleapis.com/auth/calendar.events',       # Gestión de eventos
    'https://www.googleapis.com/auth/drive',                 # Google Drive
    'https://www.googleapis.com/auth/drive.file',           # Archivos específicos en Drive
    'https://www.googleapis.com/auth/documents',            # Google Docs
    'https://www.googleapis.com/auth/documents.readonly',   # Lectura de Docs
    'https://www.googleapis.com/auth/gmail.send',           # Envío de correos
    'https://www.googleapis.com/auth/gmail.compose',        # Composición de correos
    'https://www.googleapis.com/auth/forms',                # Google Forms
    'https://www.googleapis.com/auth/forms.body',           # Contenido de Forms
    'https://www.googleapis.com/auth/forms.responses.readonly', # Lectura de respuestas
    'https://www.googleapis.com/auth/spreadsheets',         # Google Sheets
    'https://www.googleapis.com/auth/spreadsheets.readonly' # Lectura de Sheets
]

# Configuración de clientes
CLIENT_CONFIG = {
    'installed': {
        'client_id': '${CLIENT_ID}',
        'project_id': '${PROJECT_ID}',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_secret': '${CLIENT_SECRET}',
        'redirect_uris': ['urn:ietf:wg:oauth:2.0:oob', 'http://localhost']
    }
}

# Configuración de Meet
MEET_CONFIG = {
    'recording_enabled': True,
    'chat_enabled': True,
    'join_before_host': False,
    'mute_on_entry': True
}

# Configuración de Drive
DRIVE_CONFIG = {
    'root_folder_name': 'Tribunal Autónomo',
    'template_folder_name': 'Templates',
    'cases_folder_name': 'Casos',
    'backup_folder_name': 'Backups'
}

import os

# Configuración de Docs
DOCS_CONFIG = {
    'templates': {
        'acta': os.getenv('TEMPLATE_ACTA_ID', '1234567890'),  # ID de ejemplo para pruebas
        'resolucion': os.getenv('TEMPLATE_RESOLUCION_ID', '0987654321'),  # ID de ejemplo para pruebas
        'notificacion': os.getenv('TEMPLATE_NOTIFICACION_ID', '1122334455')  # ID de ejemplo para pruebas
    },
    'default_font': 'Arial',
    'default_font_size': 11
}
