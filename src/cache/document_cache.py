"""Módulo para gestión de caché de documentos."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import redis
from functools import wraps
import json
import zlib
import hashlib

class DocumentCache:
    """Gestor de caché para documentos y contenido relacionado."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hora
        self.compression_threshold = 1024  # 1KB
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generar clave de caché única."""
        return f"firstcourt:docs:{prefix}:{identifier}"
    
    def _compress_data(self, data: str) -> bytes:
        """Comprimir datos si superan el umbral."""
        data_bytes = data.encode('utf-8')
        if len(data_bytes) > self.compression_threshold:
            return zlib.compress(data_bytes)
        return data_bytes
    
    def _decompress_data(self, data: bytes) -> str:
        """Descomprimir datos si es necesario."""
        try:
            return zlib.decompress(data).decode('utf-8')
        except zlib.error:
            return data.decode('utf-8')
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Obtener documento de caché."""
        key = self._get_cache_key("doc", doc_id)
        data = self.redis.get(key)
        if data:
            return json.loads(self._decompress_data(data))
        return None
    
    async def set_document(
        self,
        doc_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Guardar documento en caché."""
        key = self._get_cache_key("doc", doc_id)
        compressed = self._compress_data(json.dumps(data))
        self.redis.set(key, compressed, ex=ttl or self.default_ttl)
    
    async def get_chunk(
        self,
        doc_id: str,
        chunk_index: int
    ) -> Optional[str]:
        """Obtener chunk de contenido."""
        key = self._get_cache_key(f"chunk:{doc_id}", str(chunk_index))
        data = self.redis.get(key)
        if data:
            return self._decompress_data(data)
        return None
    
    async def set_chunk(
        self,
        doc_id: str,
        chunk_index: int,
        content: str,
        ttl: Optional[int] = None
    ) -> None:
        """Guardar chunk de contenido."""
        key = self._get_cache_key(f"chunk:{doc_id}", str(chunk_index))
        compressed = self._compress_data(content)
        self.redis.set(key, compressed, ex=ttl or self.default_ttl)
    
    async def invalidate_document(self, doc_id: str) -> None:
        """Invalidar caché de un documento."""
        # Eliminar metadatos
        self.redis.delete(self._get_cache_key("doc", doc_id))
        
        # Eliminar chunks
        pattern = self._get_cache_key(f"chunk:{doc_id}", "*")
        chunk_keys = self.redis.keys(pattern)
        if chunk_keys:
            self.redis.delete(*chunk_keys)
    
    def cache_document(self, ttl: Optional[int] = None):
        """Decorador para cachear respuestas de documentos."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generar clave única basada en argumentos
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
                
                # Intentar obtener de caché
                cached = await self.get_document(cache_key)
                if cached:
                    return cached
                
                # Ejecutar función y cachear resultado
                result = await func(*args, **kwargs)
                await self.set_document(cache_key, result, ttl)
                return result
            return wrapper
        return decorator
    
    async def get_document_stats(self, doc_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de caché para un documento."""
        pattern = self._get_cache_key(f"*:{doc_id}", "*")
        keys = self.redis.keys(pattern)
        
        total_size = 0
        for key in keys:
            data = self.redis.get(key)
            if data:
                total_size += len(data)
        
        return {
            "cache_hits": len(keys),
            "total_size_kb": total_size / 1024,
            "compression_ratio": len(keys) > 0 and total_size / (len(keys) * 1024) or 0
        }
