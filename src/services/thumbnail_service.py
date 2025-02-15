"""Servicio de generación y gestión de miniaturas."""
import asyncio
from datetime import datetime, UTC
from typing import Optional, Dict, List
import aioredis
import boto3
from PIL import Image
from io import BytesIO

from src.cache.document_cache import DocumentCache
from src.config import settings

class ThumbnailService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL)
        self.s3 = boto3.client('s3')
        self.cache = DocumentCache()
        
        self.sizes = {
            'small': (150, 150),
            'medium': (300, 300),
            'large': (600, 600)
        }
        
        self.formats = {
            'webp': {'ext': 'webp', 'quality': 80},
            'jpeg': {'ext': 'jpg', 'quality': 85}
        }
    
    async def get_thumbnail(
        self,
        document_id: str,
        size: str = 'medium',
        format: str = 'webp',
        page: int = 1
    ) -> Optional[bytes]:
        """Obtiene la miniatura de un documento."""
        # Verificar caché
        cache_key = f"thumbnail:{document_id}:{size}:{format}:{page}"
        cached = await self.redis.get(cache_key)
        if cached:
            return cached
            
        # Generar miniatura
        thumbnail = await self._generate_thumbnail(document_id, size, format, page)
        if thumbnail:
            # Guardar en caché
            await self.redis.set(
                cache_key,
                thumbnail,
                ex=7 * 24 * 60 * 60  # 7 días
            )
            # Guardar en S3 como respaldo
            await self._store_in_s3(document_id, thumbnail, size, format, page)
            
        return thumbnail
    
    async def _generate_thumbnail(
        self,
        document_id: str,
        size: str,
        format: str,
        page: int
    ) -> Optional[bytes]:
        """Genera una miniatura del documento."""
        # Obtener documento
        document = await self.cache.get_document(document_id)
        if not document:
            return None
            
        # Convertir a imagen
        try:
            image = Image.open(BytesIO(document))
            # Redimensionar
            width, height = self.sizes[size]
            image.thumbnail((width, height))
            
            # Convertir formato
            output = BytesIO()
            image.save(
                output,
                format=self.formats[format]['ext'],
                quality=self.formats[format]['quality'],
                optimize=True
            )
            return output.getvalue()
        except Exception as e:
            print(f"Error generando miniatura: {e}")
            return None
    
    async def _store_in_s3(
        self,
        document_id: str,
        thumbnail: bytes,
        size: str,
        format: str,
        page: int
    ):
        """Almacena la miniatura en S3."""
        key = f"thumbnails/{document_id}/{size}_{format}_{page}.{self.formats[format]['ext']}"
        try:
            self.s3.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=thumbnail,
                ContentType=f"image/{self.formats[format]['ext']}"
            )
        except Exception as e:
            print(f"Error guardando en S3: {e}")
    
    async def invalidate_thumbnails(self, document_id: str):
        """Invalida todas las miniaturas de un documento."""
        pattern = f"thumbnail:{document_id}:*"
        async for key in self.redis.scan_iter(pattern):
            await self.redis.delete(key)
            
    async def prefetch_thumbnails(
        self,
        document_ids: List[str],
        size: str = 'small'
    ):
        """Pre-genera miniaturas para una lista de documentos."""
        tasks = []
        for doc_id in document_ids:
            task = asyncio.create_task(
                self.get_thumbnail(doc_id, size=size)
            )
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
