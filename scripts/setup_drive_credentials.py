import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def setup_credentials():
    """
    Setup Google Drive credentials interactively.
    This will:
    1. Start OAuth2 flow
    2. Open browser for user authentication
    3. Save credentials to credentials.json
    """
    # OAuth 2.0 scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    creds = None
    credentials_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'credentials.json'
    )
    token_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'token.json'
    )

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load client configuration
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error: {str(e)}")
                print("\nPara configurar las credenciales de Google Drive:")
                print("1. Ve a https://console.cloud.google.com/")
                print("2. Crea un nuevo proyecto o selecciona uno existente")
                print("3. Habilita la API de Google Drive")
                print("4. En 'Credenciales', crea credenciales OAuth2")
                print("5. Descarga el archivo JSON de credenciales")
                print("6. Guárdalo como 'credentials.json' en la raíz del proyecto")
                return

        # Save the credentials for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            print(f"Credenciales guardadas en {token_path}")

if __name__ == '__main__':
    setup_credentials()
