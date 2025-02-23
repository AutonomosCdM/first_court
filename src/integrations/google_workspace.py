"""
Integración con Google Workspace
"""
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleWorkspaceIntegration:
    """Cliente para integración con Google Workspace"""
    
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.pickle"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = self._get_credentials()
        
        # Inicializar servicios
        self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
        self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def _get_credentials(self) -> Credentials:
        """Obtener o refrescar credenciales de Google"""
        creds = None
        
        # Cargar token existente
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refrescar si es necesario
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    ['https://www.googleapis.com/auth/calendar',
                     'https://www.googleapis.com/auth/gmail.send',
                     'https://www.googleapis.com/auth/drive']
                )
                creds = flow.run_local_server(port=0)
            
            # Guardar token
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def schedule_hearing(self, title: str, description: str, start_time: datetime,
                        duration: timedelta, attendees: List[str]) -> Dict:
        """Programar una audiencia en Google Calendar"""
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'end': {
                'dateTime': (start_time + duration).isoformat(),
                'timeZone': 'America/Santiago',
            },
            'attendees': [{'email': email} for email in attendees],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"hearing_{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        event = self.calendar_service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        return event
    
    def send_notification(self, to: str, subject: str, body: str) -> Dict:
        """Enviar notificación por correo"""
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        return self.gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
    
    def upload_document(self, file_path: str, folder_id: Optional[str] = None) -> Dict:
        """Subir documento a Google Drive"""
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id] if folder_id else []
        }
        
        media = MediaFileUpload(
            file_path,
            resumable=True
        )
        
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        return file
    
    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Dict:
        """Crear carpeta en Google Drive"""
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []
        }
        
        folder = self.drive_service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        return folder
    
    def share_document(self, file_id: str, email: str, role: str = 'reader') -> Dict:
        """Compartir documento con otro usuario"""
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        return self.drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()
