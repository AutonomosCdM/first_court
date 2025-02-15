"""
Módulo de integración con Google Drive para la gestión documental del tribunal.
"""
from typing import Dict, List, Optional, Union
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import pickle
from datetime import datetime
from pathlib import Path

# Si modificas estos scopes, elimina el archivo token.pickle
SCOPES = [
    'https://www.googleapis.com/auth/drive'
]

class GoogleDriveClient:
    """Cliente para interactuar con Google Drive API"""
    
    def __init__(self):
        """Inicializa el cliente de Google Drive"""
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Maneja el proceso de autenticación con Google Drive"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def create_folder(self, name: str, parent_id: str = None) -> Dict:
        """
        Crea una carpeta en Google Drive
        
        Args:
            name: Nombre de la carpeta
            parent_id: ID de la carpeta padre (opcional)
            
        Returns:
            Dict con la información de la carpeta creada
        """
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        return self.service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
    
    def create_case_structure(self, case_id: str, title: str) -> Dict:
        """
        Crea la estructura de carpetas para un nuevo caso
        
        Args:
            case_id: ID del caso
            title: Título del caso
            
        Returns:
            Dict con los IDs de las carpetas creadas
        """
        # Crear carpeta principal del caso
        case_folder = self.create_folder(f"Caso-{case_id} - {title}")
        case_folder_id = case_folder['id']
        
        # Crear estructura base
        structure = {
            'public': self.create_folder('1_Documentos_Públicos', case_folder_id),
            'confidential': self.create_folder('2_Documentos_Confidenciales', case_folder_id),
            'communications': self.create_folder('3_Comunicaciones', case_folder_id)
        }
        
        # Crear subcarpetas públicas
        public_subfolders = ['Demanda', 'Contestaciones', 'Resoluciones', 'Audiencias']
        for folder in public_subfolders:
            structure[f'public_{folder.lower()}'] = self.create_folder(
                folder, structure['public']['id']
            )
        
        # Crear subcarpetas confidenciales
        confidential_subfolders = ['Juez', 'Defensor', 'Secretaría']
        for folder in confidential_subfolders:
            structure[f'confidential_{folder.lower()}'] = self.create_folder(
                folder, structure['confidential']['id']
            )
        
        # Crear subcarpetas de comunicaciones
        communication_subfolders = ['Notificaciones', 'Correspondencia']
        for folder in communication_subfolders:
            structure[f'communications_{folder.lower()}'] = self.create_folder(
                folder, structure['communications']['id']
            )
        
        return structure
    
    def upload_file(self, 
                   file_path: Union[str, Path], 
                   parent_id: str,
                   mime_type: str = None) -> Dict:
        """
        Sube un archivo a Google Drive
        
        Args:
            file_path: Ruta al archivo local
            parent_id: ID de la carpeta donde subir el archivo
            mime_type: Tipo MIME del archivo (opcional)
            
        Returns:
            Dict con la información del archivo subido
        """
        file_path = Path(file_path)
        file_metadata = {
            'name': file_path.name,
            'parents': [parent_id]
        }
        
        media = MediaFileUpload(
            str(file_path),
            mimetype=mime_type,
            resumable=True
        )
        
        return self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
    
    def set_permissions(self, 
                       file_id: str, 
                       email: str, 
                       role: str = 'reader',
                       notify: bool = True) -> Dict:
        """
        Establece permisos para un archivo o carpeta
        
        Args:
            file_id: ID del archivo o carpeta
            email: Email del usuario
            role: Rol (reader, commenter, writer, owner)
            notify: Si enviar notificación por email
            
        Returns:
            Dict con la información del permiso creado
        """
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        return self.service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=notify,
            fields='id, emailAddress, role'
        ).execute()
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Obtiene los metadatos de un archivo o carpeta
        
        Args:
            file_id: ID del archivo o carpeta
            
        Returns:
            Dict con los metadatos del archivo
        """
        return self.service.files().get(
            fileId=file_id,
            fields='id, name, mimeType, webViewLink, parents'
        ).execute()
    
    def search_files(self, 
                    query: str, 
                    parent_id: str = None,
                    file_type: str = None) -> List[Dict]:
        """
        Busca archivos en Google Drive
        
        Args:
            query: Consulta de búsqueda
            parent_id: ID de la carpeta donde buscar
            file_type: Tipo de archivo a buscar
            
        Returns:
            Lista de archivos encontrados
        """
        q = [f"name contains '{query}'"]
        
        if parent_id:
            q.append(f"'{parent_id}' in parents")
        
        if file_type:
            q.append(f"mimeType = '{file_type}'")
        
        return self.service.files().list(
            q=" and ".join(q),
            spaces='drive',
            fields='files(id, name, mimeType, webViewLink)'
        ).execute().get('files', [])
