import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, WebSocket
from unittest.mock import AsyncMock, patch
import jwt

from api.routes.ws import router
from api.middleware.auth import AuthHandler
from api.websockets.canvas_manager import canvas_manager

# Crear app de prueba
app = FastAPI()
app.include_router(router)

# Configurar auth_handler global
from api.middleware.auth import auth_handler

@pytest.fixture(scope="session", autouse=True)
def setup_auth_handler(test_settings):
    """Configure global auth_handler for tests."""
    from api.middleware.auth import auth_handler as global_handler, AuthHandler
    
    # Crear nueva instancia
    handler = AuthHandler.__new__(AuthHandler)
    handler.settings = test_settings
    handler.secret = test_settings.JWT_SECRET
    
    # Configurar instancia global
    import sys
    sys.modules['api.middleware.auth'].auth_handler = handler
    
    return handler

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def valid_token(setup_auth_handler):
    """Generar token válido usando el auth_handler global."""
    return setup_auth_handler.encode_token("test_user")

def test_websocket_connection_without_token(test_client):
    with pytest.raises(Exception) as exc:
        with test_client.websocket_connect("/ws/canvas/test_case") as websocket:
            pass
    assert "Token no proporcionado" in str(exc.value)

def test_websocket_connection_with_invalid_token(test_client):
    with pytest.raises(Exception) as exc:
        with test_client.websocket_connect("/ws/canvas/test_case?token=invalid") as websocket:
            pass
    assert "Token inválido" in str(exc.value)

@pytest.mark.asyncio
async def test_websocket_connection_with_valid_token(test_client, valid_token):
    with test_client.websocket_connect(
        f"/ws/canvas/test_case?token={valid_token}"
    ) as websocket:
        # Esperar a que la conexión sea aceptada
        data = await websocket.receive_text()
        assert "test_case" in canvas_manager.cases

@pytest.mark.asyncio
async def test_websocket_message_handling(test_client, valid_token):
    # Simular múltiples mensajes
    messages = [
        {"type": "node_update", "data": {"id": "1", "position": {"x": 100, "y": 100}}},
        {"type": "edge_create", "data": {"source": "1", "target": "2"}},
        {"type": "invalid_type", "data": {}}
    ]
    
    with test_client.websocket_connect(
        f"/ws/canvas/test_case?token={valid_token}"
    ) as websocket:
        # Esperar a que la conexión sea aceptada
        await websocket.receive_text()
        
        # Enviar mensajes
        for message in messages:
            await websocket.send_json(message)

@pytest.mark.asyncio
async def test_websocket_disconnect_handling(test_client, valid_token):
    with test_client.websocket_connect(
        f"/ws/canvas/test_case?token={valid_token}"
    ) as websocket:
        # Esperar a que la conexión sea aceptada
        await websocket.receive_text()
        assert "test_case" in canvas_manager.cases
        
        # Cerrar la conexión
        await websocket.close()
        
        # Verificar que el manager limpió la conexión
        assert "test_case" not in canvas_manager.cases
