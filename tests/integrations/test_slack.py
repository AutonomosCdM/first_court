"""
Tests para la integración con Slack
"""
import pytest
from unittest.mock import MagicMock, patch
from src.integrations.slack_integration import SlackIntegration

@pytest.fixture
def mock_slack():
    """Fixture para crear un cliente de Slack simulado"""
    with patch("slack_sdk.WebClient") as mock_client:
        client = SlackIntegration(token="xoxb-test-token")
        client.client = mock_client
        yield client

def test_send_notification(mock_slack):
    """Test para enviar notificaciones"""
    # Configurar respuesta simulada
    mock_response = {
        "ok": True,
        "channel": "C1234TEST",
        "ts": "1234567890.123456"
    }
    mock_slack.client.chat_postMessage.return_value = mock_response
    
    # Enviar notificación
    response = mock_slack.send_notification(
        channel="test-channel",
        message="Test message"
    )
    
    # Verificar que se llamó al método correcto
    mock_slack.client.chat_postMessage.assert_called_once_with(
        channel="test-channel",
        text="Test message",
        thread_ts=None,
        attachments=None
    )
    
    assert response == mock_response

def test_create_case_channel(mock_slack):
    """Test para crear un canal de caso"""
    # Configurar respuestas simuladas
    mock_channel_response = {
        "ok": True,
        "channel": {
            "id": "C1234TEST",
            "name": "caso-2025-test-001"
        }
    }
    mock_invite_response = {
        "ok": True
    }
    
    mock_slack.client.conversations_create.return_value = mock_channel_response
    mock_slack.client.conversations_invite.return_value = mock_invite_response
    
    # Crear canal
    response = mock_slack.create_case_channel(
        case_id="2025-TEST-001",
        participants=["U1234TEST", "U5678TEST"]
    )
    
    # Verificar llamadas
    mock_slack.client.conversations_create.assert_called_once_with(
        name="caso-2025-test-001",
        is_private=True
    )
    
    mock_slack.client.conversations_invite.assert_called_once_with(
        channel="C1234TEST",
        users="U1234TEST,U5678TEST"
    )
    
    assert response == mock_channel_response

def test_update_case_status(mock_slack):
    """Test para actualizar estado de caso"""
    # Configurar respuesta simulada
    mock_response = {
        "ok": True,
        "channel": "C1234TEST",
        "ts": "1234567890.123456"
    }
    mock_slack.client.chat_postMessage.return_value = mock_response
    
    # Actualizar estado
    response = mock_slack.update_case_status(
        case_id="2025-TEST-001",
        status="En Progreso",
        details="Se ha iniciado el proceso",
        channel="caso-2025-test-001"
    )
    
    # Verificar que se llamó al método con los bloques correctos
    call_args = mock_slack.client.chat_postMessage.call_args
    assert call_args is not None
    args, kwargs = call_args
    
    assert kwargs["channel"] == "caso-2025-test-001"
    assert len(kwargs["blocks"]) == 3  # Header + Status + Details
    
    # Verificar contenido de los bloques
    blocks = kwargs["blocks"]
    assert "2025-TEST-001" in blocks[0]["text"]["text"]  # Header
    assert "En Progreso" in blocks[1]["fields"][0]["text"]  # Status
    assert "Se ha iniciado el proceso" in blocks[2]["text"]["text"]  # Details

def test_send_notification_with_thread(mock_slack):
    """Test para enviar notificación en un hilo"""
    mock_response = {
        "ok": True,
        "channel": "C1234TEST",
        "ts": "1234567890.123456"
    }
    mock_slack.client.chat_postMessage.return_value = mock_response
    
    # Enviar notificación en un hilo
    response = mock_slack.send_notification(
        channel="test-channel",
        message="Reply message",
        thread_ts="1234567890.123456"
    )
    
    mock_slack.client.chat_postMessage.assert_called_once_with(
        channel="test-channel",
        text="Reply message",
        thread_ts="1234567890.123456",
        attachments=None
    )
    
    assert response == mock_response

def test_send_notification_with_attachments(mock_slack):
    """Test para enviar notificación con adjuntos"""
    mock_response = {
        "ok": True,
        "channel": "C1234TEST",
        "ts": "1234567890.123456"
    }
    mock_slack.client.chat_postMessage.return_value = mock_response
    
    attachments = [{
        "title": "Test Attachment",
        "text": "This is a test attachment",
        "color": "#36a64f"
    }]
    
    response = mock_slack.send_notification(
        channel="test-channel",
        message="Message with attachment",
        attachments=attachments
    )
    
    mock_slack.client.chat_postMessage.assert_called_once_with(
        channel="test-channel",
        text="Message with attachment",
        thread_ts=None,
        attachments=attachments
    )
    
    assert response == mock_response
