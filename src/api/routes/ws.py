from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..middleware.auth import auth_handler

router = APIRouter()

@router.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    # Aceptar la conexión primero
    await websocket.accept()
    
    try:
        # Autenticar conexión
        token = websocket.query_params.get('token')
        if not token:
            await websocket.close(code=1008, reason="Token no proporcionado")
            return
            
        try:
            user_id = auth_handler.decode_token(token)
        except Exception:
            await websocket.close(code=1008, reason="Token inválido")
            return
            
        # Enviar mensaje de bienvenida
        await websocket.send_json({"type": "welcome", "user_id": user_id})
        
        # Bucle de mensajes
        while True:
            try:
                # Recibir mensaje
                data = await websocket.receive_json()
                # Eco del mensaje
                await websocket.send_json(data)
            except WebSocketDisconnect:
                break
            
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
