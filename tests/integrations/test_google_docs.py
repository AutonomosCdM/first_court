"""
Tests for Google Docs integration
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.integrations.google_docs import GoogleDocsClient

@pytest.fixture
def mock_google_api():
    """Fixture para simular la API de Google"""
    # Respuestas simuladas
    doc_data = {
        'id': 'doc123',
        'name': 'Documento de Prueba',
        'webViewLink': 'https://docs.google.com/document/d/doc123',
        'documentId': 'doc123',
        'title': 'Documento de Prueba'
    }
    
    # Simular Drive API
    drive = MagicMock()
    drive_files = drive.files.return_value
    drive_files.create.return_value.execute.return_value = doc_data
    
    # Simular Docs API
    docs = MagicMock()
    docs_documents = docs.documents.return_value
    docs_documents.get.return_value.execute.return_value = doc_data
    
    # Simular autenticación
    auth = MagicMock()
    creds = MagicMock(universe_domain='googleapis.com')
    creds.create_scoped.return_value = creds
    creds.authorize.return_value = creds
    auth.get_credentials.return_value = creds
    
    # Crear cliente con servicios simulados
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_build.side_effect = lambda service, version, credentials: docs if service == 'docs' else drive
        client = GoogleDocsClient(auth_manager=auth)
        yield client, docs, drive

def test_crear_documento(mock_google_api):
    """Prueba la creación de un documento nuevo"""
    client, _, drive = mock_google_api
    
    # Crear documento
    doc = client.create_document("Documento de Prueba")
    
    # Verificar llamada a la API
    create_call = drive.files.return_value.create
    create_call.assert_called_once()
    args = create_call.call_args[1]
    assert args['body']['name'] == "Documento de Prueba"
    assert args['body']['mimeType'] == 'application/vnd.google-apps.document'
    
    # Verificar respuesta
    assert doc['id'] == 'doc123'
    assert doc['name'] == 'Documento de Prueba'
    assert 'webViewLink' in doc

def test_obtener_documento(mock_google_api):
    """Prueba la obtención de un documento existente"""
    client, docs, _ = mock_google_api
    
    # Obtener documento
    doc = client.get_document('doc123')
    
    # Verificar llamada a la API
    get_call = docs.documents.return_value.get
    get_call.assert_called_once_with(documentId='doc123')
    
    # Verificar respuesta
    assert doc['documentId'] == 'doc123'
    assert doc['title'] == 'Documento de Prueba'
