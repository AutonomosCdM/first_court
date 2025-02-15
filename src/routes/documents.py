"""
Endpoints para la gestión de documentos y sus funcionalidades asociadas.
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, Query
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from src.auth.auth_manager import get_current_user
from src.services.documents import DocumentService
from src.services.annotations import AnnotationService
from src.services.search import SearchService
from src.services.versions import VersionService
from src.realtime.websocket_manager import WebSocketManager
from src.monitoring.logger import Logger
from src.monitoring.metrics import document_metrics

router = APIRouter(prefix="/api/documents", tags=["documents"])
ws_manager = WebSocketManager()
logger = Logger(__name__)

# Modelos de datos
class Position(BaseModel):
    x: float
    y: float

class SearchOptions(BaseModel):
    caseSensitive: bool = False
    wholeWord: bool = False
    useRegex: bool = False

class AnnotationCreate(BaseModel):
    type: str
    content: str
    position: Position
    pageNumber: int

# Endpoints REST
@router.get("/{id}")
async def get_document(
    id: str,
    current_user = Depends(get_current_user)
) -> Dict:
    """Obtener documento por ID."""
    try:
        with document_metrics.measure_latency("get_document"):
            doc = await DocumentService.get_document(id, current_user)
            return {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "version": doc.version,
                "lastModified": doc.last_modified.isoformat(),
                "createdBy": doc.created_by,
                "permissions": doc.permissions
            }
    except Exception as e:
        logger.error(f"Error getting document {id}: {str(e)}")
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")

@router.get("/{id}/annotations")
async def get_annotations(
    id: str,
    current_user = Depends(get_current_user)
) -> Dict:
    """Obtener anotaciones de un documento."""
    try:
        with document_metrics.measure_latency("get_annotations"):
            annotations = await AnnotationService.get_annotations(id, current_user)
            return {"annotations": annotations}
    except Exception as e:
        logger.error(f"Error getting annotations for document {id}: {str(e)}")
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")

@router.post("/{id}/annotations")
async def create_annotation(
    id: str,
    annotation: AnnotationCreate,
    current_user = Depends(get_current_user)
) -> Dict:
    """Crear una nueva anotación."""
    try:
        with document_metrics.measure_latency("create_annotation"):
            result = await AnnotationService.create_annotation(
                id,
                annotation.dict(),
                current_user
            )
            return result
    except Exception as e:
        logger.error(f"Error creating annotation: {str(e)}")
        raise HTTPException(status_code=400, detail="INVALID_ANNOTATION")

@router.get("/{id}/search")
async def search_document(
    id: str,
    query: str,
    options: SearchOptions = Depends(),
    current_user = Depends(get_current_user)
) -> Dict:
    """Buscar en el contenido de un documento."""
    try:
        with document_metrics.measure_latency("search_document"):
            results = await SearchService.search_document(
                id,
                query,
                options.dict(),
                current_user
            )
            return {"results": results}
    except Exception as e:
        logger.error(f"Error searching document {id}: {str(e)}")
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")

@router.get("/{id}/versions")
async def get_versions(
    id: str,
    current_user = Depends(get_current_user)
) -> Dict:
    """Obtener historial de versiones de un documento."""
    try:
        with document_metrics.measure_latency("get_versions"):
            versions = await VersionService.get_versions(id, current_user)
            return {"versions": versions}
    except Exception as e:
        logger.error(f"Error getting versions for document {id}: {str(e)}")
        raise HTTPException(status_code=404, detail="VERSION_NOT_FOUND")

# WebSocket para colaboración en tiempo real
@router.websocket("/{id}/collaboration")
async def document_collaboration(
    websocket: WebSocket,
    id: str,
    token: str = Query(...)
):
    """WebSocket para colaboración en tiempo real."""
    try:
        # Validar token y obtener usuario
        user = await get_current_user(token)
        
        # Conectar WebSocket
        await ws_manager.connect(websocket, id, user)
        
        try:
            while True:
                # Recibir mensaje
                data = await websocket.receive_json()
                
                # Procesar según tipo de evento
                if data["type"] == "cursor_update":
                    await ws_manager.broadcast_cursor(id, user.id, data["position"])
                    
                elif data["type"] == "selection_update":
                    await ws_manager.broadcast_selection(id, user.id, data["range"])
                    
                elif data["type"] == "presence_update":
                    await ws_manager.broadcast_presence(id, user.id, data["status"])
                    
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            await ws_manager.disconnect(websocket, id, user.id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
