"""API endpoints para gestión de etiquetas."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.documents.tags import TagManager
from src.auth.auth_manager import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/tags", tags=["tags"])

# Modelos Pydantic
class TagCreate(BaseModel):
    """Modelo para crear una etiqueta."""
    name: str
    color: str
    icon: str
    metadata: Dict[str, Any] = {}

class TagUpdate(BaseModel):
    """Modelo para actualizar una etiqueta."""
    name: str | None = None
    color: str | None = None
    icon: str | None = None
    metadata: Dict[str, Any] | None = None

# Rutas
@router.post("")
async def create_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Crear una nueva etiqueta."""
    manager = TagManager()
    tag = await manager.create_tag(
        name=data.name,
        color=data.color,
        icon=data.icon,
        user_id=current_user.id,
        metadata=data.metadata
    )
    return tag

@router.get("/user")
async def get_user_tags(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Obtener etiquetas del usuario actual."""
    manager = TagManager()
    return await manager.get_user_tags(current_user.id)

@router.put("/{tag_id}")
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Actualizar una etiqueta existente."""
    manager = TagManager()
    tag = await manager.update_tag(
        tag_id=tag_id,
        user_id=current_user.id,
        updates=data.dict(exclude_unset=True)
    )
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    return tag

@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Eliminar una etiqueta."""
    manager = TagManager()
    success = await manager.delete_tag(tag_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    return {"message": "Etiqueta eliminada correctamente"}

@router.get("/stats")
async def get_tag_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obtener estadísticas de uso de etiquetas."""
    manager = TagManager()
    return await manager.get_tag_stats(current_user.id)
