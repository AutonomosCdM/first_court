"""
Cliente OAuth2 centralizado para todas las APIs de Google
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from pathlib import Path
from src.config.oauth_scopes import get_all_scopes, has_required_scopes

class OAuth2Client:
    """Cliente OAuth2 centralizado para todas las APIs de Google"""
    
    _instance = None
    
    def __new__(cls):
        """Implementa el patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(OAuth2Client, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el cliente OAuth2"""
        if self._initialized:
            return
            
        self.credentials_path = '/Users/autonomos_dev/Projects/first_court/credentials.json'
        self.token_path = '/Users/autonomos_dev/Projects/first_court/token.pickle'
        self.scopes = get_all_scopes()
        self.credentials = None
        self._services = {}
        self._initialized = True
        
        self._authenticate()
    
    def _authenticate(self):
        """Maneja el proceso de autenticación"""
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.credentials = pickle.load(token)
        
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                self.credentials = flow.run_local_server(port=0)
                
            # Guardar las credenciales para la próxima ejecución
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.credentials, token)
    
    @property
    def forms(self):
        """Obtiene el servicio de Google Forms"""
        if 'forms' not in self._services:
            self._services['forms'] = build('forms', 'v1', credentials=self.credentials)
        return self._services['forms']
    
    @property
    def sheets(self):
        """Obtiene el servicio de Google Sheets"""
        if 'sheets' not in self._services:
            self._services['sheets'] = build('sheets', 'v4', credentials=self.credentials)
        return self._services['sheets']
            

    def get_service(self, api_name, version='v3'):
        """
        Obtiene un servicio de API de Google
        
        Args:
            api_name: Nombre de la API (calendar, drive, docs, gmail)
            version: Versión de la API
            
        Returns:
            Instancia del servicio de API
        """
        service_key = f"{api_name}_{version}"
        
        if service_key not in self._services:
            self._services[service_key] = build(
                api_name, version, credentials=self.credentials)
        
        return self._services[service_key]
    
    def verify_scopes(self):
        """Verifica que tengamos todos los scopes necesarios"""
        return has_required_scopes(self.credentials)
    
    def refresh_token(self):
        """Fuerza la regeneración del token"""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self._authenticate()
        
    @property
    def calendar(self):
        """Acceso rápido al servicio de Calendar"""
        return self.get_service('calendar')
    
    @property
    def drive(self):
        """Acceso rápido al servicio de Drive"""
        return self.get_service('drive')
    
    @property
    def docs(self):
        """Acceso rápido al servicio de Docs"""
        return self.get_service('docs', 'v1')
    
    @property
    def gmail(self):
        """Acceso rápido al servicio de Gmail"""
        return self.get_service('gmail', 'v1')
