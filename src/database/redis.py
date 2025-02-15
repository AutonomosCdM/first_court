"""Redis database configuration and utilities."""
from typing import Optional
from redis import Redis
from src.config import settings

_redis_client: Optional[Redis] = None

def init_redis() -> Redis:
    """Initialize Redis connection."""
    global _redis_client
    
    if not _redis_client:
        _redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=False  # Mantener bytes para compatibilidad
        )
    
    return _redis_client

def get_redis() -> Redis:
    """Get Redis client instance."""
    if not _redis_client:
        return init_redis()
    return _redis_client

class RedisKeys:
    """Redis key patterns."""
    
    @staticmethod
    def document_presence(document_id: str) -> str:
        """Key for document presence hash."""
        return f"document:{document_id}:presence"
    
    @staticmethod
    def document_chat(document_id: str) -> str:
        """Key for document chat list."""
        return f"document:{document_id}:chat"
    
    @staticmethod
    def document_cursors(document_id: str) -> str:
        """Key for document cursors hash."""
        return f"document:{document_id}:cursors"
    
    @staticmethod
    def user_sessions(user_id: str) -> str:
        """Key for user sessions set."""
        return f"user:{user_id}:sessions"

class RedisPubSub:
    """Redis Pub/Sub channels."""
    
    DOCUMENT_UPDATES = "document_updates"
    PRESENCE_UPDATES = "presence_updates"
    CHAT_MESSAGES = "chat_messages"
    
    @staticmethod
    def document_channel(document_id: str) -> str:
        """Channel for document-specific events."""
        return f"document:{document_id}:events"
