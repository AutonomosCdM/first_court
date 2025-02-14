"""
Pruebas unitarias para la integración con Google Docs
"""
import unittest
from src.integrations.google_docs import GoogleDocsClient
from datetime import datetime

class TestGoogleDocs(unittest.TestCase):
    def setUp(self):
        """Inicializar el cliente y datos de prueba"""
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
        from src.config.google_api_config import DOCS_CONFIG
        
        doc = self.client.create_document(
            title=f"Template Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            template_id=DOCS_CONFIG['templates']['acta'],
            metadata=self.test_metadata
        )
        
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
        pdf = self.client.export_to_pdf(doc['id'])
        
        self.assertIn('id', pdf)
        self.assertIn('webViewLink', pdf)
        
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
        
        self.assertEqual(link['documentId'], doc2['id'])
        self.assertEqual(link['sourceDocumentId'], doc1['id'])
        
    def tearDown(self):
        """Limpiar recursos después de las pruebas"""
        # Aquí podríamos agregar limpieza de documentos de prueba
        pass

if __name__ == '__main__':
    unittest.main()
