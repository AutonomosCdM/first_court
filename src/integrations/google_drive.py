"""Google Drive integration module."""
from typing import List, Dict, Any, Optional, Callable
import time
import random
from functools import wraps
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from src.auth.auth_manager import AuthManager

def retry_with_backoff(max_retries: int = 10, initial_delay: float = 2.0):
    """Decorador para reintentar operaciones con backoff exponencial."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except HttpError as e:
                    if e.resp.status == 403 and 'userRateLimitExceeded' in str(e):
                        last_exception = e
                        time.sleep(delay + random.uniform(0, 2))
                        delay *= 2
                    else:
                        raise
            
            raise last_exception
        return wrapper
    return decorator

class GoogleDriveClient:
    """Client for interacting with Google Drive API."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize the Drive service."""
        credentials = self.auth_manager.get_credentials()
        self.service = build('drive', 'v3', credentials=credentials)
    
    @retry_with_backoff()
    def upload_file(self, file_path: str, folder_id: Optional[str] = None,
                    share_with: Optional[List[str]] = None,
                    title: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to Google Drive."""
        file_metadata = {'name': title if title else file_path.split('/')[-1]}
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
        media = MediaFileUpload(file_path)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        if share_with:
            for email in share_with:
                self.service.permissions().create(
                    fileId=file['id'],
                    body={
                        'type': 'user',
                        'role': 'reader',
                        'emailAddress': email
                    }
                ).execute()
        
        return file
    
    @retry_with_backoff()
    def create_folder(self, name: str, parent_id: Optional[str] = None,
                      share_with: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new folder in Google Drive."""
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        folder = self.service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        if share_with:
            for email in share_with:
                self.service.permissions().create(
                    fileId=folder['id'],
                    body={
                        'type': 'user',
                        'role': 'reader',
                        'emailAddress': email
                    }
                ).execute()
        
        return folder
    
    @retry_with_backoff()
    def create_case_structure(self, case_id: str, case_type: str = 'Civil',
                            participants: Optional[List[Dict[str, str]]] = None,
                            title: Optional[str] = None) -> Dict[str, Any]:
        """Create folder structure for a new case."""
        # Crear carpeta principal del caso
        folder_name = title if title else f"Caso {case_id} - {case_type}"
        case_folder = self.create_folder(folder_name)
        
        # Crear estructura base
        folder_structure = {
            'case_folder': case_folder,
            'subfolders': {}
        }
        
        # Emails de participantes para permisos
        participant_emails = [p['email'] for p in (participants or [])]
        
        # Crear carpetas confidenciales por rol
        if participants:
            roles = {'juez', 'defensor', 'fiscal'}
            for role in roles:
                role_emails = [p['email'] for p in participants if p.get('rol', '').lower() == role]
                if role_emails:
                    folder_name = f"Confidencial {role.title()}"
                    subfolder = self.create_folder(folder_name, case_folder['id'],
                                                 share_with=role_emails)
                    folder_structure[f'confidential_{role.lower()}'] = subfolder
        
        # Crear carpetas estándar
        standard_folders = [
            "Documentos Principales",
            "Pruebas",
            "Audiencias",
            "Resoluciones",
            "Confidencial"
        ]
        
        for folder_name in standard_folders:
            if folder_name == "Confidencial" and participants:
                judge_emails = [p['email'] for p in participants if p.get('rol', '').lower() == 'juez']
                subfolder = self.create_folder(folder_name, case_folder['id'],
                                             share_with=judge_emails)
            else:
                subfolder = self.create_folder(folder_name, case_folder['id'],
                                             share_with=participant_emails if folder_name != "Confidencial" else None)
            folder_structure['subfolders'][folder_name] = subfolder
        
        # Crear carpetas adicionales
        additional_folders = {
            'public': ('Público', participant_emails),
            'communications': ('Comunicaciones', participant_emails)
        }
        
        for key, (name, emails) in additional_folders.items():
            folder = self.create_folder(name, case_folder['id'], share_with=emails)
            folder_structure[key] = folder
        
        return folder_structure
    
    def list_files(self, folder_id: Optional[str] = None,
                  page_size: int = 10) -> List[Dict[str, Any]]:
        """List files in a folder."""
        query = f"'{folder_id}' in parents" if folder_id else None
        
        results = self.service.files().list(
            pageSize=page_size,
            fields="files(id, name, mimeType, webViewLink)",
            q=query
        ).execute()
        
        return results.get('files', [])
    
    def set_permissions(self, file_id: str, email: str, role: str = 'reader') -> Dict[str, Any]:
        """Set permissions for a file."""
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        result = self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id,emailAddress,role'
        ).execute()
        
        return result
    
    def search_files(self, query: str, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for files in Google Drive.
        
        Args:
            query: Query string using Drive search syntax
                  https://developers.google.com/drive/api/v3/search-files
            parent_id: Optional parent folder ID to search within
            
        Returns:
            List of file metadata dictionaries
        """
        q = query
        if parent_id:
            q = f"({q}) and '{parent_id}' in parents"
            
        results = self.service.files().list(
            q=q,
            spaces='drive',
            fields="files(id, name, mimeType, webViewLink, properties)"
        ).execute()
        
        return results.get('files', [])
    
    def move_file(self, file_id: str, new_parent_id: str) -> Dict[str, Any]:
        """Move a file to a different folder.
        
        Args:
            file_id: ID of the file to move
            new_parent_id: ID of the destination folder
            
        Returns:
            Updated file metadata
        """
        # Get current parents
        file = self.service.files().get(
            fileId=file_id,
            fields='parents'
        ).execute()
        
        # Remove and add parents
        previous_parents = ",".join(file.get('parents', []))
        file = self.service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields='id, name, mimeType, webViewLink, parents'
        ).execute()
        
        return file
