"""
Servicio para la gestión de miniaturas de documentos.
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import os
from PIL import Image
import io
import boto3
from src.config import settings
from src.monitoring.logger import Logger
from src.monitoring.metrics import thumbnail_metrics

logger = Logger(__name__)

class ThumbnailService:
    """Servicio para gestionar miniaturas de documentos."""
    
    def __init__(self):
        """Inicializar servicio de miniaturas."""
        self.s3 = boto3.client('s3')
        self.config = {
            'sizes': {
                'small': {'width': 150, 'height': 212},
                'medium': {'width': 300, 'height': 424},
                'large': {'width': 600, 'height': 848}
            },
            'format': {
                'type': 'webp',
                'quality': 80,
                'fallback': 'jpeg'
            },
            'generation': {
                'strategy': 'hybrid',
                'pregenerated': 5,
                'onDemand': True,
                'cacheTime': 7 * 24 * 60 * 60  # 7 días
            }
        }
        
    async def get_thumbnail(
        self,
        document_id: str,
        page: int,
        size: str = 'medium',
        format: Optional[str] = None,
        quality: Optional[int] = None
    ) -> Dict:
        """Obtener miniatura de una página.
        
        Args:
            document_id: ID del documento
            page: Número de página
            size: Tamaño de miniatura (small, medium, large)
            format: Formato de imagen (webp, jpeg)
            quality: Calidad de imagen (1-100)
            
        Returns:
            Información de la miniatura
        """
        try:
            with thumbnail_metrics.measure_latency("get_thumbnail"):
                # 1. Verificar si existe en caché
                cached = await self._get_cached_thumbnail(
                    document_id, page, size, format
                )
                if cached:
                    return cached
                
                # 2. Generar miniatura si es necesario
                if (page <= self.config['generation']['pregenerated'] or 
                    self.config['generation']['onDemand']):
                    return await self._generate_thumbnail(
                        document_id, page, size, format, quality
                    )
                    
                raise Exception("Thumbnail not available")
                
        except Exception as e:
            logger.error(f"Error getting thumbnail: {str(e)}")
            raise

    async def pregenerate_thumbnails(self, document_id: str, total_pages: int):
        """Pre-generar miniaturas para un documento.
        
        Args:
            document_id: ID del documento
            total_pages: Total de páginas
        """
        try:
            pages_to_generate = min(
                total_pages,
                self.config['generation']['pregenerated']
            )
            
            for page in range(1, pages_to_generate + 1):
                for size in self.config['sizes'].keys():
                    await self._generate_thumbnail(document_id, page, size)
                    
        except Exception as e:
            logger.error(f"Error pregenerating thumbnails: {str(e)}")

    async def invalidate_thumbnails(self, document_id: str, pages: Optional[List[int]] = None):
        """Invalidar miniaturas de un documento.
        
        Args:
            document_id: ID del documento
            pages: Lista opcional de páginas a invalidar
        """
        try:
            prefix = f"thumbnails/{document_id}"
            if pages:
                for page in pages:
                    prefix = f"thumbnails/{document_id}/{page}"
                    self._delete_s3_objects_with_prefix(prefix)
            else:
                self._delete_s3_objects_with_prefix(prefix)
                
        except Exception as e:
            logger.error(f"Error invalidating thumbnails: {str(e)}")

    async def _get_cached_thumbnail(
        self,
        document_id: str,
        page: int,
        size: str,
        format: Optional[str]
    ) -> Optional[Dict]:
        """Obtener miniatura cacheada de S3."""
        try:
            # Construir key de S3
            format = format or self.config['format']['type']
            key = f"thumbnails/{document_id}/{page}/{size}.{format}"
            
            # Verificar si existe
            try:
                self.s3.head_object(
                    Bucket=settings.S3_BUCKET,
                    Key=key
                )
            except:
                return None
            
            # Generar URL firmada
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.S3_BUCKET,
                    'Key': key
                },
                ExpiresIn=3600  # 1 hora
            )
            
            return {
                'url': url,
                'size': self.config['sizes'][size],
                'format': format,
                'expires': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting cached thumbnail: {str(e)}")
            return None

    async def _generate_thumbnail(
        self,
        document_id: str,
        page: int,
        size: str,
        format: Optional[str] = None,
        quality: Optional[int] = None
    ) -> Dict:
        """Generar miniatura de una página."""
        try:
            # 1. Obtener imagen de la página desde Google Docs
            page_image = await self._get_page_image(document_id, page)
            
            # 2. Redimensionar imagen
            target_size = self.config['sizes'][size]
            resized = self._resize_image(
                page_image,
                target_size['width'],
                target_size['height']
            )
            
            # 3. Convertir formato
            format = format or self.config['format']['type']
            quality = quality or self.config['format']['quality']
            
            output = io.BytesIO()
            if format == 'webp':
                resized.save(output, 'WEBP', quality=quality)
            else:
                resized.save(output, 'JPEG', quality=quality)
            output.seek(0)
            
            # 4. Subir a S3
            key = f"thumbnails/{document_id}/{page}/{size}.{format}"
            self.s3.upload_fileobj(
                output,
                settings.S3_BUCKET,
                key,
                ExtraArgs={
                    'ContentType': f'image/{format}',
                    'CacheControl': f'max-age={self.config["generation"]["cacheTime"]}'
                }
            )
            
            # 5. Generar URL firmada
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.S3_BUCKET,
                    'Key': key
                },
                ExpiresIn=3600
            )
            
            return {
                'url': url,
                'size': target_size,
                'format': format,
                'expires': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            raise

    async def _get_page_image(self, document_id: str, page: int) -> Image:
        """Obtener imagen de una página desde Google Docs."""
        # TODO: Implementar integración con Google Docs para exportar página como imagen
        pass

    def _resize_image(self, image: Image, width: int, height: int) -> Image:
        """Redimensionar imagen manteniendo proporción."""
        ratio = min(width/image.width, height/image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size, Image.LANCZOS)

    def _delete_s3_objects_with_prefix(self, prefix: str):
        """Eliminar objetos de S3 con un prefijo."""
        try:
            objects = self.s3.list_objects_v2(
                Bucket=settings.S3_BUCKET,
                Prefix=prefix
            )
            
            if 'Contents' in objects:
                self.s3.delete_objects(
                    Bucket=settings.S3_BUCKET,
                    Delete={
                        'Objects': [
                            {'Key': obj['Key']} 
                            for obj in objects['Contents']
                        ]
                    }
                )
                
        except Exception as e:
            logger.error(f"Error deleting S3 objects: {str(e)}")
            raise
