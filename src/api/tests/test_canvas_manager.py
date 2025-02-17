import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from api.websockets.canvas_manager import CanvasManager, CanvasConnection
from api.models.canvas import CanvasNode, CanvasEdge

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.closed = False
        
    async def send_json(self, message):
        self.sent_messages.append(message)
        
    async def close(self, code=1000):
        self.closed = True
        
    async def accept(self):
        pass

@pytest.fixture
def canvas_manager():
    return CanvasManager()

@pytest.fixture
def mock_websocket():
    return MockWebSocket()

@pytest.mark.asyncio
async def test_connect(canvas_manager, mock_websocket):
    # Test conexión exitosa
    case_id = "test_case"
    user_id = "test_user"
    
    connection_id = await canvas_manager.connect(mock_websocket, case_id, user_id)
    
    assert case_id in canvas_manager.cases
    assert connection_id in canvas_manager.cases[case_id]
    assert user_id in canvas_manager.user_connections
    assert connection_id in canvas_manager.user_connections[user_id]

@pytest.mark.asyncio
async def test_disconnect(canvas_manager, mock_websocket):
    # Setup
    case_id = "test_case"
    user_id = "test_user"
    connection_id = await canvas_manager.connect(mock_websocket, case_id, user_id)
    
    # Test desconexión
    await canvas_manager.disconnect(case_id, connection_id)
    
    assert case_id not in canvas_manager.cases
    assert user_id not in canvas_manager.user_connections

@pytest.mark.asyncio
async def test_broadcast_to_case(canvas_manager):
    # Setup
    case_id = "test_case"
    mock_ws1 = MockWebSocket()
    mock_ws2 = MockWebSocket()
    
    conn_id1 = await canvas_manager.connect(mock_ws1, case_id, "user1")
    conn_id2 = await canvas_manager.connect(mock_ws2, case_id, "user2")
    
    # Test broadcast
    test_message = {"type": "update", "data": "test"}
    await canvas_manager.broadcast_to_case(case_id, test_message)
    
    assert len(mock_ws1.sent_messages) == 1
    assert len(mock_ws2.sent_messages) == 1
    assert mock_ws1.sent_messages[0] == test_message
    assert mock_ws2.sent_messages[0] == test_message

@pytest.mark.asyncio
async def test_handle_canvas_message(canvas_manager, mock_websocket):
    # Setup
    case_id = "test_case"
    user_id = "test_user"
    connection_id = await canvas_manager.connect(mock_websocket, case_id, user_id)
    
    # Test mensaje válido
    test_message = {
        "type": "node_update",
        "data": {"id": "node1", "position": {"x": 100, "y": 100}}
    }
    
    await canvas_manager.handle_canvas_message(case_id, connection_id, test_message)
    
    # Verificar que el mensaje fue procesado y enviado
    assert len(mock_websocket.sent_messages) == 0  # No debería recibir su propio mensaje
    
    # Test mensaje inválido
    invalid_message = {"invalid": "message"}
    await canvas_manager.handle_canvas_message(case_id, connection_id, invalid_message)
    
    # Verificar que se manejó el error
    assert len(mock_websocket.sent_messages) == 0

@pytest.mark.asyncio
async def test_monitor_connections(canvas_manager, mock_websocket):
    # Setup
    case_id = "test_case"
    user_id = "test_user"
    connection_id = await canvas_manager.connect(mock_websocket, case_id, user_id)
    
    # Simular conexión antigua
    canvas_manager.cases[case_id][connection_id].last_heartbeat = (
        datetime.utcnow() - timedelta(seconds=35)
    )
    
    # Ejecutar monitor en modo test
    await canvas_manager.monitor_connections(test_mode=True)
    
    # Verificar que la conexión fue removida
    assert case_id not in canvas_manager.cases
    assert user_id not in canvas_manager.user_connections
