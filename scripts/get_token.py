"""Script para obtener token de Google OAuth2."""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
from pathlib import Path

# Scopes necesarios
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/documents'
]

def main():
    """Obtener token de Google OAuth2."""
    creds = None
    credentials_path = Path(__file__).parent.parent / 'tests/credentials'
    token_path = credentials_path / 'test_google_token.json'
    creds_path = credentials_path / 'test_google_credentials.json'

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardar credenciales
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f'Token guardado en {token_path}')

if __name__ == '__main__':
    main()
