"""
Endpoints para la gestión de miniaturas de documentos.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from src.auth.auth_manager import get_current_user
from src.services.thumbnails import ThumbnailService
from src.monitoring.logger import Logger
from src.monitoring.metrics import thumbnail_metrics

router = APIRouter(prefix="/api/documents", tags=["thumbnails"])
thumbnail_service = ThumbnailService()
logger = Logger(__name__)

@router.get("/{id}/thumbnails/{page}")
async def get_thumbnail(
    id: str,
    page: int,
    size: str = Query("medium", regex="^(small|medium|large)$"),
    format: Optional[str] = Query(None, regex="^(webp|jpeg)$"),
    quality: Optional[int] = Query(None, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Obtener miniatura de una página.
    
    Args:
        id: ID del documento
        page: Número de página
        size: Tamaño de miniatura (small, medium, large)
        format: Formato de imagen (webp, jpeg)
        quality: Calidad de imagen (1-100)
    """
    try:
        with thumbnail_metrics.measure_latency("get_thumbnail_endpoint"):
            result = await thumbnail_service.get_thumbnail(
                document_id=id,
                page=page,
                size=size,
                format=format,
                quality=quality
            )
            return result
            
    except Exception as e:
        logger.error(f"Error getting thumbnail: {str(e)}")
        raise HTTPException(status_code=404, detail="THUMBNAIL_NOT_FOUND")
