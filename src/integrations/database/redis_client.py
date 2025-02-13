"""
Cliente de Redis para caché y mensajería
"""
import json
import logging
from typing import Any, Dict, List, Optional
import redis
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        prefix: str = "first_court"
    ):
        """
        Inicializar cliente de Redis
        
        Args:
            host: Host de Redis
            port: Puerto de Redis
            db: Número de base de datos
            prefix: Prefijo para las claves
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.prefix = prefix
        
    def _key(self, key: str) -> str:
        """Generar clave con prefijo"""
        return f"{self.prefix}:{key}"
        
    def cache_set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        Guardar valor en caché
        
        Args:
            key: Clave
            value: Valor a guardar
            expire: Tiempo de expiración en segundos
        """
        try:
            full_key = self._key(key)
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
                
            self.client.set(full_key, value, ex=expire)
            logger.info(f"Valor cacheado: {key}")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Error al cachear valor: {e}")
            return False
            
    def cache_get(self, key: str) -> Any:
        """
        Obtener valor de caché
        
        Args:
            key: Clave a buscar
        """
        try:
            full_key = self._key(key)
            value = self.client.get(full_key)
            
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
                    
            return None
            
        except redis.RedisError as e:
            logger.error(f"Error al obtener valor de caché: {e}")
            return None
            
    def publish_message(
        self,
        channel: str,
        message: Dict
    ) -> bool:
        """
        Publicar mensaje en un canal
        
        Args:
            channel: Nombre del canal
            message: Mensaje a publicar
        """
        try:
            full_channel = self._key(channel)
            message_str = json.dumps(message)
            
            self.client.publish(full_channel, message_str)
            logger.info(f"Mensaje publicado en {channel}")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Error al publicar mensaje: {e}")
            return False
            
    def subscribe_to_channel(self, channel: str) -> Any:
        """
        Suscribirse a un canal
        
        Args:
            channel: Nombre del canal
        """
        try:
            pubsub = self.client.pubsub()
            full_channel = self._key(channel)
            pubsub.subscribe(full_channel)
            
            logger.info(f"Suscrito a canal: {channel}")
            return pubsub
            
        except redis.RedisError as e:
            logger.error(f"Error al suscribirse al canal: {e}")
            return None
            
    def set_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """
        Configurar rate limit
        
        Args:
            key: Clave para el rate limit
            limit: Número máximo de peticiones
            window: Ventana de tiempo en segundos
        """
        try:
            full_key = self._key(f"ratelimit:{key}")
            current = self.client.get(full_key)
            
            if current is None:
                self.client.set(full_key, 1, ex=window)
                return True
                
            count = int(current)
            if count >= limit:
                return False
                
            self.client.incr(full_key)
            return True
            
        except redis.RedisError as e:
            logger.error(f"Error en rate limit: {e}")
            return False
