from fastapi import WebSocket
from typing import Dict, List, Any
import json
import asyncio
from app.core.config import settings

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, document_id: str):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
        self.active_connections[document_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, document_id: str):
        if document_id in self.active_connections:
            self.active_connections[document_id].remove(websocket)
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]

    async def broadcast(self, document_id: str, message: Any):
        if document_id in self.active_connections:
            for connection in self.active_connections[document_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Remove dead connections
                    await self.disconnect(connection, document_id)

    async def send_personal_message(self, message: Any, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            # Handle disconnection
            for document_id, connections in self.active_connections.items():
                if websocket in connections:
                    await self.disconnect(websocket, document_id)
                    break
