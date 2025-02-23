from __future__ import annotations
import os
import logging
from typing import List, Dict, Any, Optional
from io import BytesIO

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption
from docling.exceptions import ConversionError

class DriveDoclingIntegration:
    def __init__(self, token_path: Optional[str] = None):
        """
        Initialize Drive integration with Docling
        
        Args:
            token_path (Optional[str]): Path to Google OAuth token file
        """
        self.token_path = token_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'token.json'
        )
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Docling converter with advanced options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True  # Enable OCR for scanned documents
        pipeline_options.do_table_structure = True  # Enable table structure recognition
        
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )
        
        # Authenticate and build Drive service
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with Google Drive API
        """
        try:
            if not os.path.exists(self.token_path):
                raise ValueError(
                    "Token file not found. Please run scripts/setup_drive_credentials.py first"
                )
            
            # Load credentials from token file
            creds = Credentials.from_authorized_user_file(
                self.token_path, 
                ['https://www.googleapis.com/auth/drive.readonly']
            )
            
            # Build Drive service
            self.drive_service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")

    def list_legal_documents(self, folder_id: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List legal documents from a specific Drive folder
        
        Args:
            folder_id (Optional[str]): ID of the Google Drive folder
        
        Returns:
            List of document metadata
        """
        try:
            # Define supported legal document mime types
            supported_mime_types = [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/markdown',
                'text/plain',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'text/html'
            ]
            
            # Construct query
            query = " or ".join([f"mimeType='{mime_type}'" for mime_type in supported_mime_types])
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            # Execute query
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink)'
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            self.logger.error(f"Error listing documents: {e}")
            return []

    def download_as_stream(self, file_id: str) -> BytesIO:
        """
        Download a document from Drive as a binary stream
        
        Args:
            file_id (str): Google Drive file ID
        
        Returns:
            BytesIO stream containing the document
        """
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            stream = BytesIO()
            downloader = MediaIoBaseDownload(stream, request)
            
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            stream.seek(0)
            return stream
        except Exception as e:
            self.logger.error(f"Error downloading document {file_id}: {e}")
            raise ValueError(f"Error downloading document {file_id}: {e}")

    def get_filename(self, file_id: str) -> str:
        """
        Get the filename for a Drive file
        
        Args:
            file_id (str): Google Drive file ID
        
        Returns:
            Original filename
        """
        try:
            file_metadata = self.drive_service.files().get(
                fileId=file_id,
                fields='name'
            ).execute()
            return file_metadata.get('name', 'unknown')
        except Exception as e:
            self.logger.error(f"Error getting filename for {file_id}: {e}")
            raise ValueError(f"Error getting filename for {file_id}: {e}")

    def _extract_document_text(self, document):
        """
        Extract text from a Docling document with fallback methods
        
        Args:
            document: Docling document object
        
        Returns:
            Extracted text or empty string
        """
        try:
            # Try direct text attribute
            if hasattr(document, 'text'):
                return document.text
            
            # Try markdown export
            if hasattr(document, 'export_to_markdown'):
                return document.export_to_markdown()
            
            # Try HTML export
            if hasattr(document, 'export_to_html'):
                return document.export_to_html()
            
            # Fallback to empty string
            return ""
        except Exception as e:
            self.logger.warning(f"Could not extract text: {e}")
            return ""

    def process_document(self, file_id: str) -> Dict[str, Any]:
        """
        Process a document from Drive using Docling
        
        Args:
            file_id (str): Google Drive file ID
        
        Returns:
            Processed document with content and analysis
        """
        try:
            # Download document as stream
            stream = self.download_as_stream(file_id)
            filename = self.get_filename(file_id)
            
            try:
                # Process with Docling
                result = self.converter.convert(
                    DocumentStream(name=filename, stream=stream)
                )
            except ConversionError as conv_err:
                self.logger.warning(f"Conversion error for {filename}: {conv_err}")
                return {
                    "error": f"Conversion failed: {str(conv_err)}",
                    "file_id": file_id,
                    "filename": filename
                }
            except Exception as general_err:
                self.logger.error(f"Unexpected error processing {filename}: {general_err}")
                return {
                    "error": f"Unexpected processing error: {str(general_err)}",
                    "file_id": file_id,
                    "filename": filename
                }
            
            # Extract content and metadata
            document = result.document
            
            return {
                "content": {
                    "markdown": document.export_to_markdown() if hasattr(document, 'export_to_markdown') else "",
                    "html": document.export_to_html() if hasattr(document, 'export_to_html') else "",
                    "text": self._extract_document_text(document)
                },
                "metadata": {
                    "filename": filename,
                    "format": document.format if hasattr(document, 'format') else 'Unknown',
                    "pages": document.page_count if hasattr(document, 'page_count') else 1
                },
                "analysis": {
                    "tables": [table.export_to_dataframe() for table in document.tables] if hasattr(document, 'tables') else [],
                    "images": [img.source for img in document.images] if hasattr(document, 'images') else [],
                    "structure": document.export_to_dict() if hasattr(document, 'export_to_dict') else {}
                }
            }
        except Exception as e:
            self.logger.error(f"Error processing document {file_id}: {e}")
            return {
                "error": str(e),
                "file_id": file_id,
                "filename": self.get_filename(file_id)
            }

    def process_drive_documents(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        Process all documents in a Drive folder
        
        Args:
            folder_id (str): Google Drive folder ID
        
        Returns:
            List of processed documents with analysis
        """
        # List documents
        documents = self.list_legal_documents(folder_id)
        
        # Process each document
        processed_docs = []
        for doc in documents:
            try:
                result = self.process_document(doc['id'])
                result['drive_metadata'] = doc
                processed_docs.append(result)
            except Exception as e:
                processed_docs.append({
                    'drive_metadata': doc,
                    'error': str(e)
                })
        
        return processed_docs

    def generate_document_summary(self, folder_id: str) -> Dict[str, Any]:
        """
        Generate a summary of documents in a Drive folder
        
        Args:
            folder_id (str): Google Drive folder ID
        
        Returns:
            Summary of documents in the folder
        """
        # Process documents
        processed_docs = self.process_drive_documents(folder_id)
        
        # Generate summary
        return {
            "total_documents": len(processed_docs),
            "document_summaries": [
                {
                    "filename": doc.get('drive_metadata', {}).get('name', 'Unknown'),
                    "content_length": len(doc.get('content', {}).get('text', '')),
                    "format": doc.get('metadata', {}).get('format', 'Unknown'),
                    "error": doc.get('error')
                } for doc in processed_docs
            ]
        }

# Example usage
if __name__ == "__main__":
    try:
        # Initialize Drive integration
        drive_integration = DriveDoclingIntegration()
        
        # Example: Process documents from a specific folder
        folder_id = "1fagq1gTX0E0v0g9AZ2e245t0vg8T3YIk"  # Folder ID proporcionado
        processed_documents = drive_integration.process_drive_documents(folder_id)
        
        # Print results
        for doc in processed_documents:
            print(f"Document: {doc.get('drive_metadata', {}).get('name', 'Unknown')}")
            if 'error' in doc:
                print(f"Error: {doc['error']}")
            else:
                print("Content length:", len(doc['content']['text']))
                print("Tables found:", len(doc['analysis']['tables']))
                print("Images found:", len(doc['analysis']['images']))
                print("---")
    
    except Exception as e:
        print(f"Integration error: {str(e)}")
