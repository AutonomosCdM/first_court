"""Sistema de notificaciones en tiempo real."""
from typing import Dict, Any, List, Optional, Callable
import asyncio
import json
import logging
from datetime import datetime
from dataclasses import dataclass
from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

@dataclass
class Notification:
    """Modelo de notificación."""
    id: str
    type: str
    user_id: str
    title: str
    message: str
    data: Dict[str, Any]
    created_at: datetime
    read: bool = False
    priority: str = "normal"

class NotificationManager:
    """Gestor de notificaciones."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self._handlers: Dict[str, List[Callable]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Conectar cliente WebSocket."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        try:
            # Enviar notificaciones no leídas al conectar
            unread = await self.get_unread_notifications(user_id)
            if unread:
                await websocket.send_json({
                    "type": "unread_notifications",
                    "data": unread
                })
            
            # Escuchar mensajes
            while True:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                if data["type"] == "mark_read":
                    await self.mark_as_read(user_id, data["notification_id"])
                
        except WebSocketDisconnect:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        data: Dict[str, Any] = None,
        priority: str = "normal"
    ):
        """Enviar notificación a un usuario."""
        notification = Notification(
            id=f"notif_{datetime.utcnow().timestamp()}",
            type=notification_type,
            user_id=user_id,
            title=title,
            message=message,
            data=data or {},
            created_at=datetime.utcnow(),
            priority=priority
        )
        
        # Guardar en Redis
        await self.redis.hset(
            f"notifications:{user_id}",
            notification.id,
            json.dumps({
                "id": notification.id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "created_at": notification.created_at.isoformat(),
                "read": notification.read,
                "priority": notification.priority
            })
        )
        
        # Enviar a conexiones activas
        if user_id in self.active_connections:
            notification_data = {
                "type": "new_notification",
                "data": {
                    "id": notification.id,
                    "type": notification.type,
                    "title": notification.title,
                    "message": notification.message,
                    "data": notification.data,
                    "created_at": notification.created_at.isoformat(),
                    "priority": notification.priority
                }
            }
            
            await asyncio.gather(*[
                connection.send_json(notification_data)
                for connection in self.active_connections[user_id]
            ])
        
        # Ejecutar handlers
        if notification.type in self._handlers:
            for handler in self._handlers[notification.type]:
                await handler(notification)
    
    async def get_unread_notifications(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Obtener notificaciones no leídas."""
        notifications = []
        cursor = 0
        
        while True:
            cursor, keys = await self.redis.hscan(
                f"notifications:{user_id}",
                cursor,
                count=limit
            )
            
            for _, value in keys.items():
                notif = json.loads(value)
                if not notif["read"]:
                    notifications.append(notif)
            
            if cursor == 0 or len(notifications) >= limit:
                break
        
        return sorted(
            notifications,
            key=lambda x: x["created_at"],
            reverse=True
        )[:limit]
    
    async def mark_as_read(self, user_id: str, notification_id: str):
        """Marcar notificación como leída."""
        notification_key = f"notifications:{user_id}"
        notification_data = await self.redis.hget(notification_key, notification_id)
        
        if notification_data:
            notification = json.loads(notification_data)
            notification["read"] = True
            
            await self.redis.hset(
                notification_key,
                notification_id,
                json.dumps(notification)
            )
            
            # Notificar a conexiones activas
            if user_id in self.active_connections:
                update_data = {
                    "type": "notification_read",
                    "data": {"id": notification_id}
                }
                
                await asyncio.gather(*[
                    connection.send_json(update_data)
                    for connection in self.active_connections[user_id]
                ])
    
    async def clear_old_notifications(self, days: int = 30):
        """Limpiar notificaciones antiguas."""
        cutoff = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
        
        async for key in self.redis.scan_iter("notifications:*"):
            cursor = 0
            while True:
                cursor, notifications = await self.redis.hscan(key, cursor)
                
                for notif_id, notif_data in notifications.items():
                    notification = json.loads(notif_data)
                    created_at = datetime.fromisoformat(
                        notification["created_at"]
                    ).timestamp()
                    
                    if created_at < cutoff:
                        await self.redis.hdel(key, notif_id)
                
                if cursor == 0:
                    break
    
    def register_handler(
        self,
        notification_type: str,
        handler: Callable[[Notification], None]
    ):
        """Registrar handler para tipo de notificación."""
        if notification_type not in self._handlers:
            self._handlers[notification_type] = []
        
        self._handlers[notification_type].append(handler)
    
    def unregister_handler(
        self,
        notification_type: str,
        handler: Callable[[Notification], None]
    ):
        """Eliminar handler para tipo de notificación."""
        if notification_type in self._handlers:
            self._handlers[notification_type].remove(handler)
