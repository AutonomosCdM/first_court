"""Modelo de datos para anotaciones."""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class Annotation(BaseModel):
    """Modelo de anotación en documentos."""
    
    id: str
    document_id: str
    user_id: str
    content: str
    position: Dict[str, float]  # {x, y, page}
    type: str  # note, highlight, comment
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Configuración del modelo."""
        orm_mode = True
        
    @classmethod
    async def get(cls, annotation_id: str) -> Optional['Annotation']:
        """Obtener anotación por ID."""
        # TODO: Implementar con Supabase
        pass
        
    async def save(self) -> 'Annotation':
        """Guardar anotación en la base de datos."""
        # TODO: Implementar con Supabase
        pass
        
    async def update(self, data: Dict[str, Any]) -> 'Annotation':
        """Actualizar anotación."""
        # TODO: Implementar con Supabase
        pass
        
    async def delete(self) -> bool:
        """Eliminar anotación."""
        # TODO: Implementar con Supabase
        pass
        
    @classmethod
    async def find(cls, filters: Dict[str, Any]):
        """Buscar anotaciones con filtros."""
        # TODO: Implementar con Supabase
        pass
