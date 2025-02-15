"""
Tests para la integración con Google Workspace
"""
import os
import tempfile
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any, Optional
from src.integrations.google_calendar import GoogleCalendarClient
from src.integrations.gmail import GmailClient
from src.integrations.google_drive import GoogleDriveClient

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
        
        # Configurar mock de Gmail
        mock_messages = MagicMock()
        mock_messages.send.return_value.execute.return_value = {
            'id': 'test_message_id',
            'threadId': 'test_thread_id'
        }
        mock_gmail.users.return_value.messages.return_value = mock_messages
        
        # Configurar mock de Calendar
        mock_calendar.events.return_value.insert.return_value.execute.return_value = {
            'id': 'test_event_id',
            'htmlLink': 'https://calendar.google.com/test',
            'conferenceData': {
                'entryPoints': [{
                    'uri': 'https://meet.google.com/test'
                }]
            }
        }
        
        def mock_build_service(service, version, credentials):
            if service == 'calendar':
                return mock_calendar
            elif service == 'gmail':
                return mock_gmail
            elif service == 'drive':
                return mock_drive
        
        mock_build.side_effect = mock_build_service
        
        class GoogleWorkspaceClient:
            def __init__(self):
                self.calendar = GoogleCalendarClient()
                self.gmail = GmailClient()
                self.drive = GoogleDriveClient()
                
            def schedule_hearing(self, case_id: str, title: str, start_time: datetime,
                                duration_minutes: int = 60, participants: List[str] = None,
                                description: str = None):
                summary = f"[Caso {case_id}] {title}"
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                event = {
                    'summary': summary,
                    'description': description,
                    'start': {
                        'dateTime': start_time.isoformat(),
                        'timeZone': 'America/Santiago'
                    },
                    'end': {
                        'dateTime': end_time.isoformat(),
                        'timeZone': 'America/Santiago'
                    },
                    'conferenceData': {
                        'createRequest': {
                            'requestId': f"{title}-{start_time.isoformat()}",
                            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                        }
                    }
                }
                
                if participants:
                    event['attendees'] = [{'email': email} for email in participants]
                
                return self.calendar.create_event(**event)
                
            def send_notification(self, *args, **kwargs):
                return self.gmail.send_email(*args, **kwargs)
                
            def upload_document(self, *args, **kwargs):
                return self.drive.upload_file(*args, **kwargs)
        
        client = GoogleWorkspaceClient()
        yield client, mock_calendar, mock_gmail, mock_drive

def test_schedule_hearing(mock_google_workspace):
    """Test para programar una audiencia"""
    client, mock_calendar, mock_gmail, mock_drive = mock_google_workspace
    
    # Configurar respuesta simulada para la creación del evento
    mock_event = {
        'id': 'test_event_id',
        'htmlLink': 'https://calendar.google.com/test',
        'conferenceData': {
            'entryPoints': [{
                'uri': 'https://meet.google.com/test'
            }]
        },
        'start': {'dateTime': '2025-02-15T10:00:00-03:00', 'timeZone': 'America/Santiago'},
        'end': {'dateTime': '2025-02-15T11:00:00-03:00', 'timeZone': 'America/Santiago'}
    }
    mock_calendar.events.return_value.insert.return_value.execute.return_value = mock_event
    mock_calendar.events.return_value.get.return_value.execute.return_value = mock_event
    
    # Configurar respuesta simulada para Gmail
    mock_message = {'id': 'test_message_id'}
    mock_gmail.users.return_value.messages.return_value.send.return_value.execute.return_value = mock_message
    
    # Configurar respuesta simulada para Drive
    mock_file = {'id': 'test_file_id', 'name': 'test_file.pdf'}
    mock_drive.files.return_value.create.return_value.execute.return_value = mock_file
    
    # Programar audiencia
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    participants = ['juez@test.com', 'fiscal@test.com', 'defensor@test.com']
    
    event = client.calendar.create_event(
        summary="[Caso 2025-TEST-001] Audiencia de Prueba",
        start_time=start_time,
        end_time=start_time + timedelta(minutes=60),
        attendees=participants,
        description="Esta es una audiencia de prueba",
        conference_type='hangoutsMeet'
    )
    
    # Verificar que se llamó al API correctamente
    assert mock_calendar.events.call_count > 0
    assert mock_calendar.events.return_value.insert.call_count > 0
    
    call_args = mock_calendar.events.return_value.insert.call_args
    assert call_args is not None
    
    _, kwargs = call_args
    event_body = kwargs['body']
    
    assert event_body['summary'] == "[Caso 2025-TEST-001] Audiencia de Prueba"
    assert len(event_body['attendees']) == len(participants)
    assert 'conferenceData' in event_body
    
    assert event['id'] == mock_event['id']

def test_send_notification(mock_google_workspace):
    """Test para enviar notificaciones por correo"""
    client, _, mock_gmail, _ = mock_google_workspace
    
    # Configurar respuesta simulada
    mock_response = {
        'id': '1950aba3a07ed821',
        'threadId': '1950aba3a07ed821',
        'labelIds': ['SENT']
    }
    mock_gmail.users.return_value.messages.return_value.send.return_value.execute.return_value = mock_response
    
    # Enviar notificación
    response = client.gmail.send_email(
        to="test@example.com",
        subject="Test Notification",
        body="This is a test notification",
        html_body="<p>This is a test notification</p>"
    )
    
    # Verificar llamada al API
    assert mock_gmail.users.return_value.messages.return_value.send.call_count > 0
    assert response == mock_response

def test_upload_document(mock_google_workspace):
    """Test para subir documentos a Drive"""
    client, _, _, mock_drive = mock_google_workspace
    
    # Crear archivo temporal de prueba
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp:
        temp.write("Este es un archivo de prueba")
        temp_path = temp.name
    
    # Configurar respuesta simulada para crear carpeta
    mock_folder = {
        'id': 'test_folder_id',
        'name': 'Test Folder',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    mock_drive.files.return_value.create.return_value.execute.return_value = mock_folder
    
    # Crear carpeta
    folder = client.drive.create_folder("Test Folder")
    
    # Configurar respuesta simulada para subir archivo
    mock_file = {
        'id': 'test_file_id',
        'name': 'test_document.txt',
        'webViewLink': 'https://drive.google.com/test',
        'mimeType': 'text/plain'
    }
    mock_drive.files.return_value.create.return_value.execute.return_value = mock_file
    
    # Subir documento
    response = client.drive.upload_file(
        file_path=temp_path,
        folder_id=folder['id'],
        title="Test Document"
    )
    
    # Verificar llamada al API
    assert mock_drive.files.call_count > 0
    assert mock_drive.files.return_value.create.call_count > 0
    
    call_args = mock_drive.files.return_value.create.call_args
    assert call_args is not None
    
    _, kwargs = call_args
    file_metadata = kwargs.get('body', {})
    
    assert file_metadata.get('name') == "Test Document"
    assert file_metadata['parents'] == [folder['id']]
    assert response == mock_file
    
    # Limpiar
    os.unlink(temp_path)

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
