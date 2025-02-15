"""API endpoints para notificaciones."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from datetime import datetime

from src.auth.auth_manager import get_current_user
from src.notifications.notification_manager import NotificationManager
from src.models.user import User

router = APIRouter()
notification_manager = NotificationManager()

@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user)
):
    """Endpoint WebSocket para notificaciones en tiempo real."""
    await notification_manager.connect(websocket, current_user.id)

@router.get("/notifications/unread")
async def get_unread_notifications(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Obtener notificaciones no leídas."""
    return await notification_manager.get_unread_notifications(
        current_user.id,
        limit=limit
    )

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Marcar notificación como leída."""
    await notification_manager.mark_as_read(current_user.id, notification_id)
    return {"status": "success"}

# Endpoints para pruebas y desarrollo
@router.post("/notifications/test")
async def send_test_notification(
    current_user: User = Depends(get_current_user)
):
    """Enviar notificación de prueba."""
    await notification_manager.send_notification(
        user_id=current_user.id,
        title="Notificación de prueba",
        message="Esta es una notificación de prueba",
        notification_type="test",
        data={"timestamp": datetime.utcnow().isoformat()},
        priority="normal"
    )
    return {"status": "success"}
