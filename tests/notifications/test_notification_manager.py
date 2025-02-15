"""Tests para el sistema de notificaciones."""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta, UTC
import json
from fastapi import WebSocket, WebSocketDisconnect

from src.notifications.notification_manager import (
    NotificationManager,
    Notification
)

@pytest.fixture
def redis_mock():
    """Mock de cliente Redis."""
    return AsyncMock()

@pytest.fixture
def notification_manager(redis_mock):
    """Fixture para NotificationManager."""
    with patch('redis.asyncio.Redis.from_url', return_value=redis_mock):
        manager = NotificationManager()
        manager.redis = redis_mock
        return manager

@pytest.fixture
def websocket_mock():
    """Mock de WebSocket."""
    socket = AsyncMock(spec=WebSocket)
    socket.receive_text = AsyncMock()
    socket.send_json = AsyncMock()
    return socket

@pytest.mark.asyncio
async def test_connect_websocket(notification_manager, websocket_mock, redis_mock):
    """Test conexión WebSocket."""
    # Preparar
    user_id = "test_user_1"
    unread_notifications = [
        {
            "id": "notif_1",
            "type": "test",
            "title": "Test",
            "message": "Test message",
            "created_at": datetime.utcnow().isoformat(),
            "read": False
        }
    ]
    redis_mock.hscan.return_value = (0, {"notif_1": json.dumps(unread_notifications[0])})
    
    # Simular desconexión después de enviar notificaciones
    websocket_mock.receive_text.side_effect = WebSocketDisconnect()
    
    # Ejecutar
    await notification_manager.connect(websocket_mock, user_id)
    
    # Verificar
    websocket_mock.accept.assert_called_once()
    websocket_mock.send_json.assert_called_once_with({
        "type": "unread_notifications",
        "data": unread_notifications
    })
    assert user_id not in notification_manager.active_connections

@pytest.mark.asyncio
async def test_send_notification(notification_manager, redis_mock):
    """Test envío de notificación."""
    # Preparar
    user_id = "test_user_2"
    websocket = AsyncMock(spec=WebSocket)
    notification_manager.active_connections[user_id] = [websocket]
    
    # Ejecutar
    await notification_manager.send_notification(
        user_id=user_id,
        title="Test Notification",
        message="Test message",
        notification_type="test",
        data={"key": "value"}
    )
    
    # Verificar
    redis_mock.hset.assert_called_once()
    websocket.send_json.assert_called_once()
    call_data = websocket.send_json.call_args[0][0]
    assert call_data["type"] == "new_notification"
    assert call_data["data"]["title"] == "Test Notification"

@pytest.mark.asyncio
async def test_get_unread_notifications(notification_manager, redis_mock):
    """Test obtener notificaciones no leídas."""
    # Preparar
    user_id = "test_user_3"
    notifications = {
        "notif_1": json.dumps({
            "id": "notif_1",
            "read": False,
            "created_at": datetime.utcnow().isoformat()
        }),
        "notif_2": json.dumps({
            "id": "notif_2",
            "read": True,
            "created_at": datetime.utcnow().isoformat()
        })
    }
    redis_mock.hscan.return_value = (0, notifications)
    
    # Ejecutar
    result = await notification_manager.get_unread_notifications(user_id)
    
    # Verificar
    assert len(result) == 1
    assert result[0]["id"] == "notif_1"

@pytest.mark.asyncio
async def test_mark_as_read(notification_manager, redis_mock):
    """Test marcar notificación como leída."""
    # Preparar
    user_id = "test_user_4"
    notification_id = "notif_1"
    notification_data = {
        "id": notification_id,
        "read": False,
        "created_at": datetime.utcnow().isoformat()
    }
    redis_mock.hget.return_value = json.dumps(notification_data)
    
    websocket = AsyncMock(spec=WebSocket)
    notification_manager.active_connections[user_id] = [websocket]
    
    # Ejecutar
    await notification_manager.mark_as_read(user_id, notification_id)
    
    # Verificar
    redis_mock.hset.assert_called_once()
    websocket.send_json.assert_called_once_with({
        "type": "notification_read",
        "data": {"id": notification_id}
    })

@pytest.mark.asyncio
async def test_notification_handlers(notification_manager):
    """Test handlers de notificaciones."""
    # Preparar
    handler_called = False
    notification_type = "test_handler"
    
    async def test_handler(notification: Notification):
        nonlocal handler_called
        handler_called = True
        assert notification.type == notification_type
    
    # Registrar handler
    notification_manager.register_handler(notification_type, test_handler)
    
    # Ejecutar
    await notification_manager.send_notification(
        user_id="test_user_5",
        title="Test",
        message="Test",
        notification_type=notification_type
    )
    
    # Verificar
    assert handler_called

@pytest.mark.asyncio
async def test_clear_old_notifications(notification_manager, redis_mock):
    """Test limpieza de notificaciones antiguas."""
    # Preparar
    old_date = datetime.now(UTC) - timedelta(days=31)
    now = datetime.now(UTC)
    notifications = {
        "old_notif": json.dumps({
            "id": "old_notif",
            "created_at": old_date.isoformat()
        }),
        "new_notif": json.dumps({
            "id": "new_notif",
            "created_at": now.isoformat()
        })
    }
    
    # Configurar mock de scan_iter
    async def async_iter(pattern):
        yield "notifications:test_user"
    redis_mock.scan_iter = MagicMock(return_value=async_iter("notifications:*"))
    redis_mock.hscan = AsyncMock(return_value=(0, notifications))
    
    # Ejecutar
    await notification_manager.clear_old_notifications(days=30)
    
    # Verificar
    redis_mock.hdel.assert_called_once_with(
        "notifications:test_user",
        "old_notif"
    )
