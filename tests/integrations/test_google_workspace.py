"""
Tests para la integración con Google Workspace
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from src.integrations.google_workspace import GoogleWorkspaceIntegration

@pytest.fixture
def mock_google_workspace():
    """Fixture para crear un cliente de Google Workspace simulado"""
    with patch("google.oauth2.credentials.Credentials") as mock_creds, \
         patch("google.auth.transport.requests.Request") as mock_request, \
         patch("google_auth_oauthlib.flow.InstalledAppFlow") as mock_flow, \
         patch("googleapiclient.discovery.build") as mock_build:
        
        # Simular credenciales
        mock_creds.valid = True
        mock_creds.expired = False
        
        # Simular servicios
        mock_calendar = MagicMock()
        mock_gmail = MagicMock()
        mock_drive = MagicMock()
        
        def mock_build_service(service, version, credentials):
            if service == 'calendar':
                return mock_calendar
            elif service == 'gmail':
                return mock_gmail
            elif service == 'drive':
                return mock_drive
        
        mock_build.side_effect = mock_build_service
        
        client = GoogleWorkspaceIntegration()
        client.authenticate()
        
        yield client, mock_calendar, mock_gmail, mock_drive

def test_schedule_hearing(mock_google_workspace):
    """Test para programar una audiencia"""
    client, mock_calendar, _, _ = mock_google_workspace
    
    # Configurar respuesta simulada para la creación del evento
    mock_event = {
        'id': 'test_event_id',
        'htmlLink': 'https://calendar.google.com/test',
        'conferenceData': {
            'entryPoints': [{
                'uri': 'https://meet.google.com/test'
            }]
        }
    }
    mock_calendar.events().insert().execute.return_value = mock_event
    
    # Programar audiencia
    start_time = datetime.now() + timedelta(days=1)
    participants = ['juez@test.com', 'fiscal@test.com', 'defensor@test.com']
    
    event = client.schedule_hearing(
        case_id="2025-TEST-001",
        title="Audiencia de Prueba",
        start_time=start_time,
        duration_minutes=60,
        participants=participants,
        description="Esta es una audiencia de prueba"
    )
    
    # Verificar que se llamó al API correctamente
    mock_calendar.events().insert.assert_called_once()
    call_args = mock_calendar.events().insert.call_args
    assert call_args is not None
    
    _, kwargs = call_args
    event_body = kwargs['body']
    
    assert event_body['summary'] == "[Caso 2025-TEST-001] Audiencia de Prueba"
    assert len(event_body['attendees']) == len(participants)
    assert 'conferenceData' in event_body
    
    assert event == mock_event

def test_send_notification(mock_google_workspace):
    """Test para enviar notificaciones por correo"""
    client, _, mock_gmail, _ = mock_google_workspace
    
    # Configurar respuesta simulada
    mock_response = {'id': 'test_message_id'}
    mock_gmail.users().messages().send().execute.return_value = mock_response
    
    # Enviar notificación
    response = client.send_notification(
        to="test@example.com",
        subject="Test Notification",
        body="This is a test notification"
    )
    
    # Verificar llamada al API
    mock_gmail.users().messages().send.assert_called_once()
    assert response == mock_response

def test_upload_document(mock_google_workspace):
    """Test para subir documentos a Drive"""
    client, _, _, mock_drive = mock_google_workspace
    
    # Configurar respuesta simulada
    mock_file = {
        'id': 'test_file_id',
        'name': 'test_document.pdf',
        'webViewLink': 'https://drive.google.com/test'
    }
    mock_drive.files().create().execute.return_value = mock_file
    
    # Subir documento
    response = client.upload_document(
        file_path="/path/to/test_document.pdf",
        folder_id="test_folder_id",
        title="Test Document"
    )
    
    # Verificar llamada al API
    mock_drive.files().create.assert_called_once()
    call_args = mock_drive.files().create.call_args
    assert call_args is not None
    
    _, kwargs = call_args
    file_metadata = kwargs['body']
    
    assert file_metadata['name'] == "Test Document"
    assert file_metadata['parents'] == ["test_folder_id"]
    assert response == mock_file

def test_create_folder(mock_google_workspace):
    """Test para crear carpetas en Drive"""
    _, _, _, mock_drive = mock_google_workspace
    
    # Configurar respuesta simulada
    mock_folder = {
        'id': 'test_folder_id',
        'name': 'Test Folder',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    mock_drive.files().create().execute.return_value = mock_folder
    
    # Crear carpeta
    folder_metadata = {
        'name': 'Test Folder',
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': ['parent_folder_id']
    }
    
    response = mock_drive.files().create(
        body=folder_metadata,
        fields='id, name, mimeType'
    ).execute()
    
    # Verificar respuesta
    assert response['id'] == 'test_folder_id'
    assert response['name'] == 'Test Folder'
    assert response['mimeType'] == 'application/vnd.google-apps.folder'

def test_share_document(mock_google_workspace):
    """Test para compartir documentos"""
    _, _, _, mock_drive = mock_google_workspace
    
    # Configurar respuesta simulada
    mock_permission = {
        'id': 'test_permission_id',
        'type': 'user',
        'role': 'reader'
    }
    mock_drive.permissions().create().execute.return_value = mock_permission
    
    # Crear permiso
    permission_metadata = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': 'user@test.com'
    }
    
    response = mock_drive.permissions().create(
        fileId='test_file_id',
        body=permission_metadata,
        sendNotificationEmail=True
    ).execute()
    
    # Verificar respuesta
    assert response['id'] == 'test_permission_id'
    assert response['type'] == 'user'
    assert response['role'] == 'reader'
