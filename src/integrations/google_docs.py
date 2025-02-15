"""Google Docs integration module."""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from src.auth.auth_manager import AuthManager
from src.utils.diff import calculate_diff, apply_patch

class GoogleDocsClient:
    """Client for interacting with Google Docs API."""
    
    def __init__(self, auth_manager=None):
        """Initialize the Google Docs client.
        
        Args:
            auth_manager: Optional AuthManager instance. If not provided,
                         a new one will be created.
        """
        self.auth_manager = auth_manager or AuthManager()
        self.service = None
        self.drive_service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize the Docs and Drive services."""
        credentials = self.auth_manager.get_credentials()
        self.service = build('docs', 'v1', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)
    
    def create_document(self, title: str, metadata: Optional[Dict[str, Any]] = None,
                       template_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Google Doc, optionally from a template.
        
        Args:
            title: Title of the document
            metadata: Optional metadata to add to the document
            template_id: Optional template document ID to copy from
            
        Returns:
            Dict containing document information including id, name, and webViewLink
        """
        if template_id:
            # Copiar desde plantilla
            file_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.document'
            }
            doc = self.drive_service.files().copy(
                fileId=template_id,
                body=file_metadata,
                fields='id,name,mimeType,webViewLink'
            ).execute()
        else:
            # Crear documento nuevo
            doc_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.document'
            }
            doc = self.drive_service.files().create(
                body=doc_metadata,
                fields='id,name,mimeType,webViewLink'
            ).execute()
        
        if metadata:
            # Actualizar metadatos
            self.drive_service.files().update(
                fileId=doc['id'],
                body={'properties': metadata},
                fields='id,name,mimeType,webViewLink'
            ).execute()
        
        return doc
    
    def get_document(self, document_id: str, include_content: bool = True) -> Dict[str, Any]:
        """Get a Google Doc by ID with optional content.
        
        Args:
            document_id: ID of the document
            include_content: Whether to include document content
            
        Returns:
            Document metadata and optionally content
        """
        fields = 'documentId,title,revisionId'
        if include_content:
            fields += ',body'
            
        return self.service.documents().get(
            documentId=document_id,
            fields=fields
        ).execute()
    
    def insert_text(self, document_id: str, text: str,
                   index: int = 1) -> Dict[str, Any]:
        """Insert text into a Google Doc at specified index."""
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': index
                    },
                    'text': text
                }
            }
        ]
        
        result = self.service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return result
    
    def get_document_version(self, document_id: str, revision_id: str) -> Dict[str, Any]:
        """Get a specific version of a document.
        
        Args:
            document_id: ID of the document
            revision_id: ID of the revision to retrieve
            
        Returns:
            Document content at specified revision
        """
        return self.drive_service.revisions().get(
            fileId=document_id,
            revisionId=revision_id,
            fields='id,modifiedTime,lastModifyingUser'
        ).execute()
    
    def list_document_versions(self, document_id: str) -> List[Dict[str, Any]]:
        """List all versions of a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of document versions with metadata
        """
        return self.drive_service.revisions().list(
            fileId=document_id,
            fields='revisions(id,modifiedTime,lastModifyingUser)'
        ).execute().get('revisions', [])
    
    def restore_document_version(self, document_id: str, revision_id: str) -> Dict[str, Any]:
        """Restore a document to a previous version.
        
        Args:
            document_id: ID of the document
            revision_id: ID of the revision to restore
            
        Returns:
            Updated document metadata
        """
        return self.drive_service.revisions().update(
            fileId=document_id,
            revisionId=revision_id,
            body={'published': True}
        ).execute()
    
    def get_document_changes(self, document_id: str, start_revision_id: str,
                           end_revision_id: str) -> List[Dict[str, Any]]:
        """Get changes between two document versions.
        
        Args:
            document_id: ID of the document
            start_revision_id: Starting revision ID
            end_revision_id: Ending revision ID
            
        Returns:
            List of changes between versions
        """
        start_content = self.get_document(document_id, revision_id=start_revision_id)
        end_content = self.get_document(document_id, revision_id=end_revision_id)
        
        return calculate_diff(start_content, end_content)
    
    def replace_text(self, document_id: str,
                    replacements: Dict[str, str]) -> Dict[str, Any]:
        """Replace text in a Google Doc using a dictionary of replacements."""
        requests = []
        for old_text, new_text in replacements.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': old_text,
                        'matchCase': True
                    },
                    'replaceText': new_text
                }
            })
            
        result = self.service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return result
    
    def create_document_link(self, doc_id: str = None, source_doc_id: str = None) -> str:
        """Get the web view link for a document.
        
        Args:
            doc_id: Document ID (deprecated, use source_doc_id instead)
            source_doc_id: Document ID to get link for
            
        Returns:
            Web view link for the document
        """
        file_id = source_doc_id or doc_id
        if not file_id:
            raise ValueError("Either doc_id or source_doc_id must be provided")
            
        file = self.drive_service.files().get(
            fileId=file_id,
            fields='webViewLink'
        ).execute()
        return file['webViewLink']
    
    def export_to_pdf(self, document_id: str) -> bytes:
        """Export a Google Doc to PDF format."""
        request = self.drive_service.files().export_media(
            fileId=document_id,
            mimeType='application/pdf'
        )
        
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
        return file.getvalue()
