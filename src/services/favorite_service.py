"""Servicio de gestión de favoritos."""
from datetime import datetime, UTC
from typing import List, Dict, Optional
import aioredis
from supabase import create_client

from src.config import settings

class FavoriteService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL)
        self.supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    async def add_favorite(
        self,
        user_id: str,
        document_id: str,
        device_id: Optional[str] = None
    ) -> bool:
        """Marca un documento como favorito."""
        try:
            # Insertar en Supabase
            data = {
                'user_id': user_id,
                'document_id': document_id,
                'device_id': device_id,
                'added_at': datetime.now(UTC).isoformat()
            }
            self.supabase.table('document_favorites').insert(data).execute()
            
            # Actualizar caché
            cache_key = f"favorites:{user_id}"
            await self.redis.sadd(cache_key, document_id)
            
            return True
        except Exception as e:
            print(f"Error agregando favorito: {e}")
            return False
    
    async def remove_favorite(
        self,
        user_id: str,
        document_id: str
    ) -> bool:
        """Elimina un documento de favoritos."""
        try:
            # Eliminar de Supabase
            self.supabase.table('document_favorites')\
                .delete()\
                .match({'user_id': user_id, 'document_id': document_id})\
                .execute()
            
            # Actualizar caché
            cache_key = f"favorites:{user_id}"
            await self.redis.srem(cache_key, document_id)
            
            return True
        except Exception as e:
            print(f"Error eliminando favorito: {e}")
            return False
    
    async def get_favorites(self, user_id: str) -> List[str]:
        """Obtiene la lista de documentos favoritos del usuario."""
        cache_key = f"favorites:{user_id}"
        
        # Intentar obtener de caché
        cached = await self.redis.smembers(cache_key)
        if cached:
            return list(cached)
        
        # Obtener de Supabase
        try:
            response = self.supabase.table('document_favorites')\
                .select('document_id')\
                .match({'user_id': user_id})\
                .execute()
            
            favorites = [item['document_id'] for item in response.data]
            
            # Actualizar caché
            if favorites:
                await self.redis.sadd(cache_key, *favorites)
                await self.redis.expire(cache_key, 24 * 60 * 60)  # 24 horas
            
            return favorites
        except Exception as e:
            print(f"Error obteniendo favoritos: {e}")
            return []
    
    async def sync_favorites(
        self,
        user_id: str,
        changes: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Sincroniza cambios en favoritos entre dispositivos."""
        try:
            # Procesar documentos agregados
            for doc_id in changes.get('added', []):
                await self.add_favorite(user_id, doc_id)
            
            # Procesar documentos eliminados
            for doc_id in changes.get('removed', []):
                await self.remove_favorite(user_id, doc_id)
            
            # Obtener lista actualizada
            current_favorites = await self.get_favorites(user_id)
            
            return {
                'favorites': current_favorites,
                'timestamp': datetime.now(UTC).isoformat()
            }
        except Exception as e:
            print(f"Error sincronizando favoritos: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(UTC).isoformat()
            }
