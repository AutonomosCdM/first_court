"""WebSocket manager for real-time collaboration."""
from typing import Dict, Set, Any, Optional
import json
from fastapi import WebSocket, WebSocketDisconnect
from redis import Redis
from src.config import settings

class ConnectionManager:
    """Manage WebSocket connections and real-time collaboration."""
    
    def __init__(self, redis_client: Redis):
        """Initialize the connection manager."""
        self.redis = redis_client
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.document_participants: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, document_id: str, user_id: str):
        """Connect a user to a document's collaboration session."""
        await websocket.accept()
        
        # Inicializar estructuras si no existen
        if document_id not in self.active_connections:
            self.active_connections[document_id] = {}
            self.document_participants[document_id] = set()
            
        # Agregar conexión
        self.active_connections[document_id][user_id] = websocket
        self.document_participants[document_id].add(user_id)
        
        # Actualizar presencia en Redis
        self.redis.hset(
            f"document:{document_id}:presence",
            user_id,
            json.dumps({
                "status": "active",
                "last_activity": "now"
            })
        )
        
        # Notificar a otros usuarios
        await self.broadcast_to_document(
            document_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "participants": list(self.document_participants[document_id])
            },
            exclude_user=None  # Enviar a todos, incluido el nuevo usuario
        )
    
    async def disconnect(self, document_id: str, user_id: str):
        """Disconnect a user from a document's collaboration session."""
        # Eliminar conexión
        if document_id in self.active_connections:
            self.active_connections[document_id].pop(user_id, None)
            self.document_participants[document_id].discard(user_id)
            
            # Limpiar si no hay más participantes
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]
                del self.document_participants[document_id]
        
        # Actualizar presencia en Redis
        self.redis.hdel(f"document:{document_id}:presence", user_id)
        
        # Notificar a otros usuarios
        await self.broadcast_to_document(
            document_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "participants": list(self.document_participants.get(document_id, set()))
            }
        )
    
    async def broadcast_to_document(self, document_id: str, message: Dict[str, Any],
                                  exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a document."""
        if document_id in self.active_connections:
            for user_id, connection in self.active_connections[document_id].items():
                if exclude_user and user_id == exclude_user:
                    continue
                    
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    await self.disconnect(document_id, user_id)
    
    async def send_cursor_position(self, document_id: str, user_id: str,
                                 position: Dict[str, Any]):
        """Broadcast cursor position to other users."""
        message = {
            "type": "cursor_position",
            "user_id": user_id,
            "position": position
        }
        await self.broadcast_to_document(document_id, message, exclude_user=user_id)
    
    async def send_document_update(self, document_id: str, user_id: str,
                                 update: Dict[str, Any]):
        """Broadcast document updates to all users."""
        message = {
            "type": "document_update",
            "user_id": user_id,
            "update": update
        }
        await self.broadcast_to_document(document_id, message)
    
    async def send_chat_message(self, document_id: str, user_id: str,
                              content: str, message_type: str = "text"):
        """Send a chat message to all users in a document."""
        message = {
            "type": "chat_message",
            "user_id": user_id,
            "content": content,
            "message_type": message_type,
            "timestamp": "now"
        }
        
        # Guardar mensaje en Redis
        self.redis.rpush(
            f"document:{document_id}:chat",
            json.dumps(message)
        )
        
        await self.broadcast_to_document(document_id, message)
    
    def get_document_participants(self, document_id: str) -> Set[str]:
        """Get all active participants in a document."""
        return self.document_participants.get(document_id, set())
    
    def get_user_presence(self, document_id: str) -> Dict[str, Any]:
        """Get presence information for all users in a document."""
        presence = self.redis.hgetall(f"document:{document_id}:presence")
        return {
            k.decode(): json.loads(v.decode())
            for k, v in presence.items()
        }
