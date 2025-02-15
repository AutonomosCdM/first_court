"""
Centralized authentication manager for First Court.
Handles all OAuth2 credentials and token management.
"""
import os
import json
import pickle
from pathlib import Path
from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from src.config.oauth_scopes import get_all_scopes

class AuthManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.project_root = Path('/Users/autonomos_dev/Projects/first_court')
            
            # Usar credenciales de prueba si están configuradas
            if os.getenv('GOOGLE_CREDENTIALS_FILE') and os.getenv('GOOGLE_TOKEN_FILE'):
                self.credentials_path = Path(os.getenv('GOOGLE_CREDENTIALS_FILE'))
                self.token_path = Path(os.getenv('GOOGLE_TOKEN_FILE'))
            else:
                self.credentials_path = self.project_root / 'credentials.json'
                self.token_path = self.project_root / 'token.pickle'
            self.credentials: Optional[Credentials] = None
            self.scopes = get_all_scopes()
            self.initialized = True
    
    def get_credentials(self) -> Credentials:
        """Get valid credentials, refreshing or creating new ones if necessary."""
        if self.credentials and self.credentials.valid:
            return self.credentials
            
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
        else:
            if self.token_path.exists():
                # Intentar cargar como pickle primero
                try:
                    with open(self.token_path, 'rb') as token:
                        self.credentials = pickle.load(token)
                except:
                    # Si falla, intentar como JSON
                    with open(self.token_path, 'r') as token:
                        token_data = json.loads(token.read())
                        self.credentials = Credentials.from_authorized_user_info(token_data, self.scopes)
                    
            if not self.credentials or not self.credentials.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.scopes)
                self.credentials = flow.run_local_server(port=0)
                
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)
                    
        return self.credentials
    
    def clear_credentials(self):
        """Clear stored credentials and token."""
        if self.token_path.exists():
            self.token_path.unlink()
        self.credentials = None
