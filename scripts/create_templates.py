"""
Script para crear los templates necesarios en Google Drive
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import json
from pathlib import Path

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents'
]

def get_credentials():
    """Obtiene las credenciales de Google"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_template(service, creds, template_name, template_content):
    """Crea un template en Google Drive"""
    file_metadata = {
        'name': template_name,
        'mimeType': 'application/vnd.google-apps.document'
    }
    
    file = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()
    
    # Leer contenido del template local
    template_path = Path('src/integrations/templates') / template_content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Actualizar el documento con el contenido
    doc_service = build('docs', 'v1', credentials=creds)
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': content
            }
        }
    ]
    
    doc_service.documents().batchUpdate(
        documentId=file['id'],
        body={'requests': requests}
    ).execute()
    
    return file['id']

def main():
    """Función principal para crear templates"""
    print("\n=== Creando templates en Google Drive ===\n")
    
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    templates = {
        'Acta de Audiencia': 'acta_audiencia.html',
        'Resolución': 'resolucion.html',
        'Notificación': 'notificacion.html'
    }
    
    template_ids = {}
    
    for name, content_file in templates.items():
        print(f"\nCreando template: {name}")
        try:
            template_id = create_template(service, creds, name, content_file)
            template_ids[name] = template_id
            print(f"✓ Template creado con ID: {template_id}")
        except Exception as e:
            print(f"⚠ Error al crear template {name}: {str(e)}")
    
    # Guardar IDs en archivo de configuración
    config_path = Path('src/config/template_ids.json')
    with open(config_path, 'w') as f:
        json.dump(template_ids, f, indent=2)
    
    print(f"\n✓ IDs guardados en {config_path}")
    print("\nPor favor, actualice estos IDs en src/config/google_api_config.py")

if __name__ == '__main__':
    main()
