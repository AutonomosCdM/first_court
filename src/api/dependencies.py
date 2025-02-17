from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .middleware.auth import auth_handler

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Obtiene el usuario actual a partir del token JWT"""
    try:
        user_id = auth_handler.decode_token(credentials.credentials)
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

def get_db():
    """Mock de conexión a base de datos para pruebas"""
    return {}
