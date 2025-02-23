from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from typing import Optional
import jwt
from ..config import get_settings

security = HTTPBearer()

class AuthHandler:
    def __init__(self):
        self.settings = get_settings()
        self.secret = self.settings.JWT_SECRET

    def encode_token(self, user_id: str) -> str:
        """Genera un token JWT para el usuario"""
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token: str) -> str:
        """Decodifica y valida un token JWT"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expirado')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Token inválido')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)) -> str:
        """Middleware para validar token en requests"""
        return self.decode_token(auth.credentials)

# Obtener instancia de AuthHandler
def get_auth_handler():
    return AuthHandler()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Dependency para obtener el usuario actual"""
    try:
        user_id = auth_handler.decode_token(credentials.credentials)
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )
