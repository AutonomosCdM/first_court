"""
Tests para la integración con Redis
"""
import pytest
import json
from src.integrations.database.redis_client import RedisClient

@pytest.fixture
def redis_client():
    """Fixture para crear un cliente de Redis de prueba"""
    client = RedisClient(
        prefix="test_first_court"
    )
    # Limpiar datos de pruebas anteriores
    keys = client.client.keys(f"{client.prefix}:*")
    if keys:
        client.client.delete(*keys)
    return client

def test_cache_operations(redis_client):
    """Test para operaciones básicas de caché"""
    # Test con string
    assert redis_client.cache_set("test_key", "test_value")
    assert redis_client.cache_get("test_key") == "test_value"
    
    # Test con diccionario
    test_dict = {"name": "Test", "value": 123}
    assert redis_client.cache_set("test_dict", test_dict)
    assert redis_client.cache_get("test_dict") == test_dict
    
    # Test con lista
    test_list = ["item1", "item2", "item3"]
    assert redis_client.cache_set("test_list", test_list)
    assert redis_client.cache_get("test_list") == test_list

def test_cache_expiration(redis_client):
    """Test para expiración de caché"""
    import time
    
    # Guardar con expiración de 1 segundo
    assert redis_client.cache_set("expire_key", "expire_value", expire=1)
    assert redis_client.cache_get("expire_key") == "expire_value"
    
    # Esperar a que expire
    time.sleep(1.1)
    assert redis_client.cache_get("expire_key") is None

def test_pubsub(redis_client):
    """Test para publicación/suscripción"""
    # Crear suscriptor
    pubsub = redis_client.subscribe_to_channel("test_channel")
    assert pubsub is not None
    
    # Publicar mensaje
    test_message = {"event": "test", "data": "message"}
    assert redis_client.publish_message("test_channel", test_message)
    
    # Recibir mensaje
    message = pubsub.get_message(timeout=1)
    assert message is not None
    if message["type"] == "message":
        received = json.loads(message["data"])
        assert received == test_message

def test_rate_limit(redis_client):
    """Test para rate limiting"""
    # Configurar rate limit: 3 requests/segundo
    key = "test_rate_limit"
    limit = 3
    window = 1
    
    # Primeras 3 peticiones deberían ser exitosas
    for _ in range(limit):
        assert redis_client.set_rate_limit(key, limit, window)
    
    # La cuarta petición debería fallar
    assert not redis_client.set_rate_limit(key, limit, window)
    
    # Esperar a que se resetee el rate limit
    import time
    time.sleep(window + 0.1)
    
    # Debería poder hacer una nueva petición
    assert redis_client.set_rate_limit(key, limit, window)

def test_key_prefixing(redis_client):
    """Test para verificar el prefijo de las claves"""
    test_key = "prefix_test"
    redis_client.cache_set(test_key, "test")
    
    # Verificar que la clave existe con el prefijo
    full_key = f"{redis_client.prefix}:{test_key}"
    assert redis_client.client.exists(full_key)
    
    # Verificar que podemos obtener el valor con la clave sin prefijo
    assert redis_client.cache_get(test_key) == "test"
