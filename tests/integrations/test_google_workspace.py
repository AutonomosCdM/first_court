"""
Tests para la integración con Google Workspace
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from src.integrations.google_workspace import GoogleWorkspaceIntegration

@pytest.fixture
def mock_google_workspace(mocker):
    """Fixture para crear un cliente de Google Workspace simulado"""
    # Simular servicios
    mock_calendar = mocker.MagicMock()
    mock_gmail = mocker.MagicMock()
    mock_drive = mocker.MagicMock()
    
    # Configurar Calendar Service
    mock_calendar_events = mocker.MagicMock()
    mock_calendar.events = mocker.MagicMock(return_value=mock_calendar_events)
    mock_calendar_events.insert = mocker.MagicMock(return_value=mock_calendar_events)
    mock_calendar_events.execute = mocker.MagicMock(return_value={
        'id': 'test_event_id',
        'htmlLink': 'https://meet.google.com/test'
    })
    
    # Configurar Gmail Service
    mock_gmail_messages = mocker.MagicMock()
    mock_gmail_users = mocker.MagicMock()
    mock_gmail_messages.send = mocker.MagicMock()
    mock_gmail_messages.send().execute = mocker.MagicMock(return_value={
        'id': 'test_message_id'
    })
    mock_gmail_users.messages = mocker.MagicMock(return_value=mock_gmail_messages)
    mock_gmail.users = mocker.MagicMock(return_value=mock_gmail_users)
    
    # Configurar Drive Service
    mock_drive_files = mocker.MagicMock()
    mock_drive_permissions = mocker.MagicMock()
    
    # Configurar respuestas para archivos y carpetas
    mock_file_response = {
        'id': 'test_file_id',
        'name': 'test_file.pdf',
        'webViewLink': 'https://drive.google.com/test'
    }
    
    mock_folder_response = {
        'id': 'test_folder_id',
        'name': 'Test Folder',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    # Configurar create().execute() para archivos y carpetas
    mock_file_execute = mocker.MagicMock(return_value=mock_file_response)
    mock_folder_execute = mocker.MagicMock(return_value=mock_folder_response)
    
    mock_file_create = mocker.MagicMock()
    mock_folder_create = mocker.MagicMock()
    
    mock_file_create.execute = mock_file_execute
    mock_folder_create.execute = mock_folder_execute
    
    # Configurar create() para devolver el mock correcto según el tipo
    def mock_create(**kwargs):
        if kwargs.get('body', {}).get('mimeType') == 'application/vnd.google-apps.folder':
            return mock_folder_create
        return mock_file_create
    
    mock_drive_files.create = mocker.MagicMock(side_effect=mock_create)
    mock_drive.files = mocker.MagicMock(return_value=mock_drive_files)
    
    # Configurar permisos
    mock_permission_execute = mocker.MagicMock(return_value={
        'id': 'test_permission_id',
        'type': 'user',
        'role': 'reader'
    })
    
    mock_permission_create = mocker.MagicMock()
    mock_permission_create.execute = mock_permission_execute
    
    mock_drive_permissions.create = mocker.MagicMock(return_value=mock_permission_create)
    mock_drive.permissions = mocker.MagicMock(return_value=mock_drive_permissions)
    
    # Crear cliente simulado
    with patch.object(GoogleWorkspaceIntegration, '_get_credentials') as mock_get_creds:
        mock_get_creds.return_value = mocker.MagicMock()
        client = GoogleWorkspaceIntegration()
        client.calendar_service = mock_calendar
        client.gmail_service = mock_gmail
        client.drive_service = mock_drive
    
    return client


def test_schedule_hearing(mock_google_workspace):
    """Test para programar una audiencia"""
    client = mock_google_workspace
    
    # Programar audiencia
    start_time = datetime.now() + timedelta(days=1)
    participants = ['juez@test.com', 'fiscal@test.com', 'defensor@test.com']
    
    event = client.schedule_hearing(
        title="Audiencia de Prueba",
        description="Esta es una audiencia de prueba",
        start_time=start_time,
        duration=timedelta(minutes=60),
        attendees=participants
    )
    
    # Verificar respuesta
    assert event['id'] == 'test_event_id'
    assert event['htmlLink'] == 'https://meet.google.com/test'

def test_send_notification(mock_google_workspace):
    """Test para enviar notificaciones por correo"""
    client = mock_google_workspace
    
    # Enviar notificación
    response = client.send_notification(
        to="test@example.com",
        subject="Test Notification",
        body="This is a test notification"
    )
    
    # Verificar respuesta
    assert response['id'] == 'test_message_id'

def test_upload_document(mock_google_workspace, tmp_path):
    """Test para subir documentos a Drive"""
    client = mock_google_workspace
    
    # Crear archivo temporal para la prueba
    test_file = tmp_path / "test_document.pdf"
    test_file.write_text("Test content")
    
    # Subir documento
    response = client.upload_document(
        file_path=str(test_file),
        folder_id="test_folder_id"
    )
    
    # Verificar llamada al API
    assert client.drive_service.files.call_count == 1
    assert client.drive_service.files().create.call_count == 1
    
    # Verificar respuesta
    assert response['id'] == 'test_file_id'
    assert response['name'] == 'test_file.pdf'
    assert response['webViewLink'] == 'https://drive.google.com/test'

def test_create_folder(mock_google_workspace):
    """Test para crear carpetas en Drive"""
    client = mock_google_workspace
    
    # Crear carpeta
    response = client.create_folder(
        name="Test Folder",
        parent_id="parent_folder_id"
    )
    
    # Verificar respuesta
    assert response['id'] == 'test_folder_id'
    assert response['name'] == 'Test Folder'
    assert response['mimeType'] == 'application/vnd.google-apps.folder'

def test_share_document(mock_google_workspace):
    """Test para compartir documentos"""
    client = mock_google_workspace
    
    # Compartir documento
    response = client.share_document(
        file_id="test_file_id",
        email="user@test.com",
        role="reader"
    )
    
    # Verificar respuesta
    assert response['id'] == 'test_permission_id'
    assert response['type'] == 'user'
    assert response['role'] == 'reader'
