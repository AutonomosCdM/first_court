"""
Procesador de documentos para el sistema RAG
"""
from typing import List, Dict, Optional
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.auth.oauth_client import OAuth2Client
import re
import html2text

class DocumentProcessor:
    """Procesa documentos de Google Docs para extraer y estructurar su contenido"""
    
    def __init__(self):
        """Inicializa el procesador de documentos"""
        self.oauth_client = OAuth2Client()
        self.docs_service = self.oauth_client.docs
        self.drive_service = self.oauth_client.drive
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True
        
    def convert_pdf_to_doc(self, pdf_id: str) -> str:
        """
        Convierte un PDF a Google Docs
        
        Args:
            pdf_id: ID del archivo PDF en Drive
            
        Returns:
            ID del documento de Google Docs creado
        """
        try:
            # Obtener metadatos del PDF
            pdf_file = self.drive_service.files().get(
                fileId=pdf_id,
                fields='name'
            ).execute()
            
            # Crear documento de Google Docs
            file_metadata = {
                'name': pdf_file['name'].replace('.pdf', ''),
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            # Copiar el PDF como Google Docs
            doc = self.drive_service.files().copy(
                fileId=pdf_id,
                body=file_metadata
            ).execute()
            
            return doc['id']
            
        except Exception as e:
            print(f"Error al convertir PDF {pdf_id}: {str(e)}")
            return None
    
    def get_document_content(self, doc_id: str) -> Dict:
        """
        Obtiene el contenido de un documento de Google Docs
        
        Args:
            doc_id: ID del documento de Google Docs
            
        Returns:
            Dict con el contenido estructurado del documento
        """
        try:
            # Obtener documento
            document = self.docs_service.documents().get(documentId=doc_id).execute()
            
            # Extraer contenido
            content = self._extract_content(document)
            metadata = self._extract_metadata(document)
            
            return {
                'doc_id': doc_id,
                'title': document.get('title', ''),
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Error al procesar documento {doc_id}: {str(e)}")
            return None
    
    def _extract_content(self, document: Dict) -> List[Dict]:
        """
        Extrae el contenido estructurado de un documento
        
        Args:
            document: Documento de Google Docs
            
        Returns:
            Lista de secciones con su contenido
        """
        content = []
        current_section = {
            'heading': 'Main',
            'content': '',
            'style': 'NORMAL'
        }
        
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                para = element['paragraph']
                
                # Obtener estilo
                style = para.get('paragraphStyle', {}).get('namedStyleType', 'NORMAL')
                
                # Obtener texto
                text = ''
                for item in para.get('elements', []):
                    if 'textRun' in item:
                        text += item['textRun'].get('content', '')
                
                # Si es un encabezado, crear nueva sección
                if style.startswith('HEADING'):
                    if current_section['content'].strip():
                        content.append(current_section)
                    current_section = {
                        'heading': text.strip(),
                        'content': '',
                        'style': style
                    }
                else:
                    current_section['content'] += text
        
        # Agregar última sección
        if current_section['content'].strip():
            content.append(current_section)
        
        return content
    
    def _extract_metadata(self, document: Dict) -> Dict:
        """
        Extrae metadatos del documento
        
        Args:
            document: Documento de Google Docs
            
        Returns:
            Dict con metadatos
        """
        # Extraer metadatos básicos
        metadata = {
            'title': document.get('title', ''),
            'revision_id': document.get('revisionId', ''),
            'document_id': document.get('documentId', ''),
            'document_style': document.get('documentStyle', {}),
        }
        
        # Extraer metadatos personalizados si existen
        try:
            properties = self.drive_service.files().get(
                fileId=document['documentId'],
                fields='properties'
            ).execute()
            
            if 'properties' in properties:
                metadata['custom'] = properties['properties']
        except:
            metadata['custom'] = {}
        
        return metadata
    
    def process_document_batch(self, doc_ids: List[str]) -> List[Dict]:
        """
        Procesa un lote de documentos
        
        Args:
            doc_ids: Lista de IDs de documentos
            
        Returns:
            Lista de documentos procesados
        """
        results = []
        for doc_id in doc_ids:
            result = self.get_document_content(doc_id)
            if result:
                results.append(result)
        return results
