from fastapi import WebSocket, HTTPException
from ..middleware.auth import auth_handler
from typing import Optional

async def get_token_from_query(websocket: WebSocket) -> Optional[str]:
    """Extrae el token JWT de los parámetros de query del WebSocket"""
    try:
        token = websocket.query_params.get('token')
        if not token:
            return None
        return token
    except Exception:
        return None

async def authenticate_ws(websocket: WebSocket) -> str:
    """Autentica una conexión WebSocket"""
    token = await get_token_from_query(websocket)
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    try:
        # Importar auth_handler aquí para asegurar que esté inicializado
        from ..middleware.auth import auth_handler
        if not auth_handler:
            raise HTTPException(status_code=500, detail="Auth handler no inicializado")
            
        user_id = auth_handler.decode_token(token)
        return user_id
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")
