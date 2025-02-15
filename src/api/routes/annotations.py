"""API endpoints para gestión de anotaciones."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from src.documents.annotations import AnnotationManager
from src.documents.annotation_filters import (
    AnnotationFilter, AnnotationFilterEngine,
    SortField, SortOrder
)
from src.documents.pdf_exporter import AnnotationPDFExporter
from src.auth.auth_manager import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/annotations", tags=["annotations"])

# Modelos Pydantic
class PositionModel(BaseModel):
    """Modelo para la posición de una anotación."""
    x: float
    y: float
    page: int

class AnnotationCreate(BaseModel):
    """Modelo para crear una anotación."""
    document_id: str
    content: str
    position: PositionModel
    type: str = "note"
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

class AnnotationUpdate(BaseModel):
    """Modelo para actualizar una anotación."""
    content: Optional[str] = None
    position: Optional[PositionModel] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class AnnotationSearchParams(BaseModel):
    """Parámetros de búsqueda avanzada."""
    content_query: Optional[str] = None
    tags: Optional[List[str]] = None
    types: Optional[List[str]] = None
    users: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    page_range: Optional[tuple[int, int]] = None
    position_box: Optional[Dict[str, float]] = None
    sort_by: SortField = SortField.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    limit: int = 50
    offset: int = 0

# Rutas
@router.post("")
async def create_annotation(
    data: AnnotationCreate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Crear una nueva anotación."""
    try:
        manager = AnnotationManager()
        annotation = await manager.create_annotation(
            document_id=data.document_id,
            user=current_user,
            content=data.content,
            position=data.position.dict(),
            type=data.type,
            tags=data.tags,
            metadata=data.metadata
        )
        return annotation.dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/document/{document_id}/search")
async def search_annotations(
    document_id: str,
    params: AnnotationSearchParams,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Búsqueda avanzada de anotaciones."""
    try:
        manager = AnnotationManager()
        filter_engine = AnnotationFilterEngine()
        
        # Obtener todas las anotaciones del documento
        annotations = await manager.get_annotations(document_id)
        
        # Crear filtro
        annotation_filter = AnnotationFilter(
            content_query=params.content_query,
            tags=params.tags,
            types=params.types,
            users=params.users,
            created_after=params.created_after,
            created_before=params.created_before,
            updated_after=params.updated_after,
            updated_before=params.updated_before,
            page_range=params.page_range,
            position_box=params.position_box,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            limit=params.limit,
            offset=params.offset
        )
        
        # Aplicar filtros
        filtered_annotations = filter_engine.apply_filter(
            annotations,
            annotation_filter
        )
        
        return {
            "total": len(annotations),
            "filtered": len(filtered_annotations),
            "annotations": [a.dict() for a in filtered_annotations]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/document/{document_id}/export")
async def export_annotations(
    document_id: str,
    format: str = "pdf",
    current_user: User = Depends(get_current_user)
) -> Response:
    """Exportar anotaciones a PDF."""
    try:
        if format != "pdf":
            raise HTTPException(
                status_code=400,
                detail="Formato no soportado"
            )
        
        manager = AnnotationManager()
        annotations = await manager.get_annotations(document_id)
        
        if not annotations:
            raise HTTPException(
                status_code=404,
                detail="No hay anotaciones para exportar"
            )
        
        # Obtener información del documento
        doc_info = await manager.get_document_info(document_id)
        
        # Exportar a PDF
        exporter = AnnotationPDFExporter()
        pdf_content = await exporter.export_annotations(
            annotations=[a.dict() for a in annotations],
            doc_info=doc_info
        )
        
        return Response(
            content=pdf_content.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=annotations_{document_id}.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{annotation_id}")
async def update_annotation(
    annotation_id: str,
    data: AnnotationUpdate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Actualizar una anotación existente."""
    try:
        manager = AnnotationManager()
        annotation = await manager.update_annotation(
            annotation_id=annotation_id,
            user=current_user,
            updates=data.dict(exclude_unset=True)
        )
        if not annotation:
            raise HTTPException(status_code=404, detail="Anotación no encontrada")
        return annotation.dict()
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{annotation_id}")
async def delete_annotation(
    annotation_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Eliminar una anotación."""
    try:
        manager = AnnotationManager()
        success = await manager.delete_annotation(
            annotation_id=annotation_id,
            user=current_user
        )
        if not success:
            raise HTTPException(status_code=404, detail="Anotación no encontrada")
        return {"message": "Anotación eliminada correctamente"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/document/{document_id}/summary")
async def get_annotation_summary(
    document_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obtener resumen de anotaciones de un documento."""
    manager = AnnotationManager()
    return await manager.get_annotation_summary(document_id)
