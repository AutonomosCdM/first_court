"""
Script para verificar y configurar las APIs de Google necesarias
"""
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path

def verify_credentials():
    """Verifica que las credenciales existan y sean válidas"""
    creds_path = Path('/Users/autonomos_dev/Projects/first_court/credentials.json')
    if not creds_path.exists():
        raise FileNotFoundError("No se encontró el archivo credentials.json")
    
    print("✓ Archivo credentials.json encontrado")
    return True

def verify_token():
    """Verifica el token de autenticación"""
    token_path = Path('token.pickle')
    if token_path.exists():
        print("✓ Token existente encontrado")
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            if creds and creds.valid:
                print("✓ Token válido")
                return True
    
    print("⚠ Se necesita generar un nuevo token")
    return False

def verify_apis():
    """Verifica que las APIs necesarias estén habilitadas"""
    required_apis = [
        'calendar-json.googleapis.com',
        'docs.googleapis.com',
        'drive.googleapis.com',
        'gmail.googleapis.com'
    ]
    
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
    
    service = build('serviceusage', 'v1', credentials=creds)
    
    project = 'projects/your-project-id'
    enabled_apis = []
    
    try:
        request = service.services().list(parent=project, filter='state:ENABLED')
        while request is not None:
            response = request.execute()
            enabled_apis.extend([s['name'] for s in response.get('services', [])])
            request = service.services().list_next(request, response)
    except Exception as e:
        print(f"⚠ Error al verificar APIs: {str(e)}")
        return False
    
    missing_apis = [api for api in required_apis if api not in enabled_apis]
    
    if missing_apis:
        print("⚠ Las siguientes APIs necesitan ser habilitadas:")
        for api in missing_apis:
            print(f"  - {api}")
        return False
    
    print("✓ Todas las APIs necesarias están habilitadas")
    return True

def verify_templates():
    """Verifica que los templates existan"""
    from src.config.google_api_config import DOCS_CONFIG
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        return False
    
    drive_service = build('drive', 'v3', credentials=creds)
    
    for template_name, template_id in DOCS_CONFIG['templates'].items():
        try:
            drive_service.files().get(fileId=template_id).execute()
            print(f"✓ Template {template_name} encontrado")
        except Exception as e:
            print(f"⚠ Template {template_name} no encontrado: {str(e)}")
            return False
    
    return True

def main():
    """Función principal de verificación"""
    print("\n=== Verificando configuración de Google APIs ===\n")
    
    checks = [
        ("Credenciales", verify_credentials),
        ("Token", verify_token),
        ("APIs", verify_apis),
        ("Templates", verify_templates)
    ]
    
    all_passed = True
    
    for name, check in checks:
        print(f"\nVerificando {name}...")
        try:
            if not check():
                all_passed = False
                print(f"⚠ Verificación de {name} falló")
        except Exception as e:
            all_passed = False
            print(f"⚠ Error en verificación de {name}: {str(e)}")
    
    if all_passed:
        print("\n✓ Todas las verificaciones pasaron exitosamente!")
    else:
        print("\n⚠ Algunas verificaciones fallaron. Por favor revise los mensajes anteriores.")

if __name__ == '__main__':
    main()
