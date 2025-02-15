"""Real-time collaboration endpoints."""
from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from redis import Redis

from src.realtime.websocket_manager import ConnectionManager
from src.database import get_redis
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/ws", tags=["realtime"])

# Instancia global del manager
manager: ConnectionManager = None

@router.on_event("startup")
async def startup_event():
    """Initialize the connection manager on startup."""
    global manager
    redis = get_redis()
    manager = ConnectionManager(redis)

@router.websocket("/documents/{document_id}/collaboration")
async def document_collaboration(
    websocket: WebSocket,
    document_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """WebSocket endpoint for document collaboration."""
    try:
        await manager.connect(websocket, str(document_id), str(current_user['id']))
        
        while True:
            try:
                data = await websocket.receive_json()
                
                # Manejar diferentes tipos de mensajes
                if data['type'] == 'cursor_position':
                    await manager.send_cursor_position(
                        str(document_id),
                        str(current_user['id']),
                        data['position']
                    )
                    
                elif data['type'] == 'document_update':
                    await manager.send_document_update(
                        str(document_id),
                        str(current_user['id']),
                        data['update']
                    )
                    
                elif data['type'] == 'chat_message':
                    await manager.send_chat_message(
                        str(document_id),
                        str(current_user['id']),
                        data['content'],
                        data.get('message_type', 'text')
                    )
                    
            except WebSocketDisconnect:
                break
                
    finally:
        await manager.disconnect(str(document_id), str(current_user['id']))

@router.get("/documents/{document_id}/presence")
async def get_document_presence(
    document_id: UUID,
    redis: Redis = Depends(get_redis),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get presence information for a document."""
    if not manager:
        return {"participants": [], "presence": {}}
        
    return {
        "participants": list(manager.get_document_participants(str(document_id))),
        "presence": manager.get_user_presence(str(document_id))
    }

@router.get("/documents/{document_id}/chat")
async def get_document_chat(
    document_id: UUID,
    limit: int = 50,
    redis: Redis = Depends(get_redis),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get recent chat messages for a document."""
    messages = redis.lrange(f"document:{document_id}:chat", -limit, -1)
    return {
        "messages": [
            json.loads(msg.decode())
            for msg in messages
        ]
    }
