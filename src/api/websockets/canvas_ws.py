from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
from ..models.canvas import CanvasNode, CanvasEdge, CanvasLayout

class CanvasWebsocketManager:
    def __init__(self):
        # case_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, case_id: str):
        await websocket.accept()
        if case_id not in self.active_connections:
            self.active_connections[case_id] = set()
        self.active_connections[case_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, case_id: str):
        self.active_connections[case_id].remove(websocket)
        if not self.active_connections[case_id]:
            del self.active_connections[case_id]
    
    async def broadcast_to_case(self, case_id: str, message: dict):
        if case_id in self.active_connections:
            for connection in self.active_connections[case_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    await self.disconnect(connection, case_id)

canvas_ws_manager = CanvasWebsocketManager()

async def handle_canvas_websocket(websocket: WebSocket, case_id: str):
    await canvas_ws_manager.connect(websocket, case_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Validar el tipo de evento
            event_type = data.get("type")
            if not event_type:
                continue
                
            # Preparar mensaje para broadcast
            message = {
                "type": event_type,
                "data": data.get("data", {}),
                "timestamp": data.get("timestamp")
            }
            
            # Broadcast a todos los clientes del caso
            await canvas_ws_manager.broadcast_to_case(case_id, message)
            
    except WebSocketDisconnect:
        canvas_ws_manager.disconnect(websocket, case_id)
    except Exception as e:
        print(f"Error in canvas websocket: {str(e)}")
        canvas_ws_manager.disconnect(websocket, case_id)
