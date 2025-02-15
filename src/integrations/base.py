"""
Base class for Google API integrations
"""
import os
from typing import Optional, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleApiBase:
    """Base class for all Google API clients"""
    
    def __init__(self, service_name: str, version: str, scopes: list[str]):
        self.service_name = service_name
        self.version = version
        self.scopes = scopes
        self.credentials = self._get_credentials()
        self.service = self._build_service()
    
    def _get_credentials(self) -> Credentials:
        """Get or refresh credentials"""
        creds = None
        token_path = 'token.pickle'
        credentials_path = 'credentials.json'

        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh/create token if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds
    
    def _build_service(self) -> Any:
        """Build the service object"""
        return build(
            self.service_name,
            self.version,
            credentials=self.credentials
        )
    
    def _execute_request(self, request: Any) -> Any:
        """Execute a request with error handling"""
        try:
            return request.execute()
        except Exception as e:
            # Log error details
            print(f"Error executing {self.service_name} request: {str(e)}")
            raise
