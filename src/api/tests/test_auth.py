import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt

from src.api.middleware.auth import AuthHandler
from src.api.config import get_settings

@pytest.fixture
def test_user_id():
    return "test_user_123"

def test_encode_token(auth_handler, test_user_id):
    token = auth_handler.encode_token(test_user_id)
    assert isinstance(token, str)
    
    # Verificar que el token puede ser decodificado
    payload = jwt.decode(token, auth_handler.secret, algorithms=['HS256'])
    assert payload['sub'] == test_user_id
    assert 'exp' in payload
    assert 'iat' in payload

def test_decode_token(auth_handler, test_user_id):
    # Generar token válido
    token = auth_handler.encode_token(test_user_id)
    
    # Verificar decodificación exitosa
    decoded_user_id = auth_handler.decode_token(token)
    assert decoded_user_id == test_user_id

def test_decode_expired_token(auth_handler, test_user_id):
    # Generar token expirado
    payload = {
        'exp': datetime.utcnow() - timedelta(hours=1),
        'iat': datetime.utcnow() - timedelta(hours=2),
        'sub': test_user_id
    }
    expired_token = jwt.encode(payload, auth_handler.secret, algorithm='HS256')
    
    # Verificar que se lanza excepción
    with pytest.raises(HTTPException) as exc:
        auth_handler.decode_token(expired_token)
    assert exc.value.status_code == 401
    assert 'Token expirado' in str(exc.value.detail)

def test_decode_invalid_token(auth_handler):
    # Intentar decodificar token inválido
    with pytest.raises(HTTPException) as exc:
        auth_handler.decode_token("invalid_token")
    assert exc.value.status_code == 401
    assert 'Token inválido' in str(exc.value.detail)

def test_auth_wrapper(auth_handler):
    # Simular credenciales
    class MockCredentials:
        def __init__(self, token):
            self.credentials = token
    
    # Test con token válido
    token = auth_handler.encode_token("test_user")
    user_id = auth_handler.auth_wrapper(MockCredentials(token))
    assert user_id == "test_user"
    
    # Test con token inválido
    with pytest.raises(HTTPException):
        auth_handler.auth_wrapper(MockCredentials("invalid_token"))

def test_get_current_user(auth_handler, test_user_id):
    # Simular credenciales
    class MockCredentials:
        def __init__(self, token):
            self.credentials = token
    
    # Test con token válido
    token = auth_handler.encode_token(test_user_id)
    credentials = MockCredentials(token)
    
    # Verificar que se obtiene el usuario correctamente
    user_id = auth_handler.auth_wrapper(credentials)
    assert user_id == test_user_id
