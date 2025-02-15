"""
Módulo de integración con Google Docs para la gestión de documentos judiciales.
"""
from typing import Dict, List, Optional, Union
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime
from pathlib import Path
import json

# Si modificas estos scopes, elimina el archivo token.pickle
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]

class GoogleDocsClient:
    """Cliente para interactuar con Google Docs"""
    
    def __init__(self):
        """Inicializa el cliente de Google Docs"""
        self.creds = None
        self.docs_service = None
        self.drive_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Maneja el proceso de autenticación"""
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
        
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
    
    def create_document(self, 
                       title: str,
                       template_id: str = None,
                       folder_id: str = None,
                       metadata: Dict = None) -> Dict:
        """
        Crea un nuevo documento en Google Docs
        
        Args:
            title: Título del documento
            template_id: ID del template a usar (opcional)
            folder_id: ID de la carpeta donde crear el documento
            metadata: Metadata adicional del documento
            
        Returns:
            Dict con la información del documento creado
        """
        # Crear documento base
        doc_metadata = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        if folder_id:
            doc_metadata['parents'] = [folder_id]
        
        doc = self.drive_service.files().create(
            body=doc_metadata,
            fields='id, webViewLink'
        ).execute()
        
        # Si hay template, copiar su contenido
        if template_id:
            template = self.docs_service.documents().get(
                documentId=template_id
            ).execute()
            
            # Copiar contenido del template
            requests = self._generate_template_copy_requests(template)
            self.docs_service.documents().batchUpdate(
                documentId=doc['id'],
                body={'requests': requests}
            ).execute()
        
        # Agregar metadata como propiedades personalizadas
        if metadata:
            self.drive_service.files().update(
                fileId=doc['id'],
                body={'properties': metadata}
            ).execute()
        
        return doc
    
    def export_to_pdf(self, 
                     doc_id: str,
                     output_folder_id: str = None) -> Dict:
        """
        Exporta un documento de Google Docs a PDF
        
        Args:
            doc_id: ID del documento a exportar
            output_folder_id: ID de la carpeta donde guardar el PDF
            
        Returns:
            Dict con la información del PDF creado
        """
        # Obtener metadata del documento original
        doc_metadata = self.drive_service.files().get(
            fileId=doc_id,
            fields='name, properties'
        ).execute()
        
        # Configurar metadata del PDF
        pdf_metadata = {
            'name': f"{doc_metadata['name']}.pdf",
            'mimeType': 'application/pdf'
        }
        
        if output_folder_id:
            pdf_metadata['parents'] = [output_folder_id]
        
        # Exportar a PDF
        pdf = self.drive_service.files().export(
            fileId=doc_id,
            mimeType='application/pdf'
        ).execute()
        
        # Crear archivo PDF en Drive
        pdf_file = self.drive_service.files().create(
            body=pdf_metadata,
            media_body=pdf,
            fields='id, webViewLink'
        ).execute()
        
        # Copiar propiedades personalizadas
        if 'properties' in doc_metadata:
            self.drive_service.files().update(
                fileId=pdf_file['id'],
                body={'properties': doc_metadata['properties']}
            ).execute()
        
        return pdf_file
    
    def create_document_link(self,
                           doc_id: str,
                           source_doc_id: str = None) -> Dict:
        """
        Crea un enlace entre documentos relacionados
        
        Args:
            doc_id: ID del documento principal
            source_doc_id: ID del documento fuente
            
        Returns:
            Dict con la información del enlace
        """
        if source_doc_id:
            # Obtener metadata de ambos documentos
            doc = self.drive_service.files().get(
                fileId=doc_id,
                fields='properties'
            ).execute()
            
            source = self.drive_service.files().get(
                fileId=source_doc_id,
                fields='properties'
            ).execute()
            
            # Actualizar propiedades para mantener referencias
            doc_props = doc.get('properties', {})
            doc_props['sourceDocumentId'] = source_doc_id
            
            source_props = source.get('properties', {})
            source_props['derivedDocumentId'] = doc_id
            
            # Actualizar ambos documentos
            self.drive_service.files().update(
                fileId=doc_id,
                body={'properties': doc_props}
            ).execute()
            
            self.drive_service.files().update(
                fileId=source_doc_id,
                body={'properties': source_props}
            ).execute()
        
        return {
            'documentId': doc_id,
            'sourceDocumentId': source_doc_id
        }
    
    def _generate_template_copy_requests(self, template: Dict) -> List[Dict]:
        """Genera las solicitudes para copiar un template"""
        requests = []
        
        # Insertar contenido del template
        if 'body' in template:
            for element in template['body'].get('content', []):
                if 'paragraph' in element:
                    requests.append({
                        'insertText': {
                            'location': {
                                'index': 1
                            },
                            'text': element['paragraph']['elements'][0]['textRun']['content']
                        }
                    })
        
        return requests
