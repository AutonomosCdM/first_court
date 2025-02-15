"""
Pruebas unitarias para la integración con Google Docs
"""
import unittest
from unittest.mock import MagicMock, patch
from src.integrations.google_docs import GoogleDocsClient
from datetime import datetime

class TestGoogleDocs(unittest.TestCase):
    def setUp(self):
        """Inicializar el cliente y datos de prueba"""
        # Mock Drive service
        self.mock_drive_service = MagicMock()
        self.mock_drive_service.files = MagicMock()
        
        # Mock file creation response
        create_response = {
            'id': 'test_doc_id',
            'name': 'Test Document',
            'webViewLink': 'https://docs.google.com/document/d/test'
        }
        create_request = MagicMock()
        create_request.execute.return_value = create_response
        self.mock_drive_service.files.create.return_value = create_request
        
        # Mock file copy response
        copy_response = {
            'id': 'test_copy_id',
            'name': 'Test Copy',
            'webViewLink': 'https://docs.google.com/document/d/copy'
        }
        copy_request = MagicMock()
        copy_request.execute.return_value = copy_response
        self.mock_drive_service.files.copy.return_value = copy_request
        
        # Mock template response
        template_response = {
            'id': 'test_template_id',
            'name': 'Test Template',
            'mimeType': 'application/vnd.google-apps.document',
            'webViewLink': 'https://docs.google.com/document/d/template'
        }
        get_request = MagicMock()
        get_request.execute.return_value = template_response
        self.mock_drive_service.files.get.return_value = get_request
        
        # Mock Docs service
        self.mock_docs_service = MagicMock()
        
        # Create client with mocked services
        with patch('googleapiclient.discovery.build') as mock_build:
            def mock_build_service(service, version, credentials):
                if service == 'drive':
                    return self.mock_drive_service
                elif service == 'docs':
                    return self.mock_docs_service
            mock_build.side_effect = mock_build_service
            
            self.client = GoogleDocsClient()
        
        self.test_metadata = {
            'case_id': 'TEST-2025-003',
            'type': 'Acta',
            'created_by': 'test_suite'
        }
        
    def test_create_document(self):
        """Prueba la creación de un documento"""
        doc = self.client.create_document(
            title=f"Test Document - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            metadata=self.test_metadata
        )
        
        self.assertIn('id', doc)
        self.assertIn('webViewLink', doc)
        
    def test_create_from_template(self):
        """Prueba la creación de un documento desde template"""
        template_id = 'test_template_id'
        title = f"Template Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create document from template
        doc = self.client.create_document(
            title=title,
            template_id=template_id,
            metadata=self.test_metadata
        )
        
        # Verify API calls
        self.mock_drive_service.files.get.assert_called_once_with(
            fileId=template_id,
            fields='id,name,mimeType,webViewLink'
        )
        
        self.mock_drive_service.files.copy.assert_called_once()
        
        self.assertIn('id', doc)
        self.assertIn('webViewLink', doc)
        
    def test_export_to_pdf(self):
        """Prueba la exportación a PDF"""
        # Crear documento para exportar
        doc = self.client.create_document(
            title=f"PDF Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            metadata=self.test_metadata
        )
        
        # Exportar a PDF
        pdf_bytes = self.client.export_to_pdf(doc['id'])
        
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
        
    def test_document_link(self):
        """Prueba la creación de enlaces entre documentos"""
        # Crear dos documentos
        doc1 = self.client.create_document(
            title=f"Source Doc - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            metadata=self.test_metadata
        )
        
        doc2 = self.client.create_document(
            title=f"Target Doc - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            metadata=self.test_metadata
        )
        
        # Crear enlace
        link = self.client.create_document_link(
            doc_id=doc2['id'],
            source_doc_id=doc1['id']
        )
        
        self.assertIsInstance(link, str)
        self.assertTrue(link.startswith('https://docs.google.com/document/d/'))
        
    def tearDown(self):
        """Limpiar recursos después de las pruebas"""
        # Aquí podríamos agregar limpieza de documentos de prueba
        pass

if __name__ == '__main__':
    unittest.main()
