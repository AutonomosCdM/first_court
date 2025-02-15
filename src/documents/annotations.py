"""Módulo para gestionar anotaciones en documentos."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from src.integrations.google_drive import GoogleDriveClient
from src.database.models import Annotation, User

class AnnotationManager:
    """Gestor de anotaciones para documentos."""
    
    def __init__(self):
        """Inicializar el gestor de anotaciones."""
        self.drive_client = GoogleDriveClient()
    
    async def create_annotation(
        self,
        document_id: str,
        user: User,
        content: str,
        position: Dict[str, float],
        type: str = "note",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Annotation:
        """Crear una nueva anotación en un documento.
        
        Args:
            document_id: ID del documento
            user: Usuario que crea la anotación
            content: Contenido de la anotación
            position: Posición en el documento {x, y, page}
            type: Tipo de anotación (note, highlight, comment)
            metadata: Metadatos adicionales
            
        Returns:
            Annotation: Nueva anotación creada
        """
        annotation = Annotation(
            id=str(uuid4()),
            document_id=document_id,
            user_id=user.id,
            content=content,
            position=position,
            type=type,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Verificar permisos en el documento
        file = self.drive_client.get_file(document_id)
        if not file:
            raise ValueError(f"Documento no encontrado: {document_id}")
            
        # Guardar anotación en base de datos
        await annotation.save()
        
        return annotation
    
    async def get_annotations(
        self,
        document_id: str,
        user: Optional[User] = None,
        type: Optional[str] = None,
        page: Optional[int] = None
    ) -> List[Annotation]:
        """Obtener anotaciones de un documento.
        
        Args:
            document_id: ID del documento
            user: Filtrar por usuario específico
            type: Filtrar por tipo de anotación
            page: Filtrar por número de página
            
        Returns:
            List[Annotation]: Lista de anotaciones
        """
        filters = {"document_id": document_id}
        
        if user:
            filters["user_id"] = user.id
        if type:
            filters["type"] = type
        if page is not None:
            filters["position.page"] = page
            
        annotations = await Annotation.find(filters).sort("created_at", -1).to_list()
        return annotations
    
    async def update_annotation(
        self,
        annotation_id: str,
        user: User,
        updates: Dict[str, Any]
    ) -> Optional[Annotation]:
        """Actualizar una anotación existente.
        
        Args:
            annotation_id: ID de la anotación
            user: Usuario que realiza la actualización
            updates: Campos a actualizar
            
        Returns:
            Optional[Annotation]: Anotación actualizada o None si no existe
        """
        annotation = await Annotation.get(annotation_id)
        if not annotation:
            return None
            
        # Verificar permisos
        if annotation.user_id != user.id:
            raise PermissionError("No tiene permisos para editar esta anotación")
            
        # Actualizar campos permitidos
        allowed_fields = {"content", "position", "metadata"}
        update_data = {k: v for k, v in updates.items() if k in allowed_fields}
        update_data["updated_at"] = datetime.utcnow()
        
        await annotation.update(update_data)
        return annotation
    
    async def delete_annotation(
        self,
        annotation_id: str,
        user: User
    ) -> bool:
        """Eliminar una anotación.
        
        Args:
            annotation_id: ID de la anotación
            user: Usuario que realiza la eliminación
            
        Returns:
            bool: True si se eliminó correctamente
        """
        annotation = await Annotation.get(annotation_id)
        if not annotation:
            return False
            
        # Verificar permisos
        if annotation.user_id != user.id:
            raise PermissionError("No tiene permisos para eliminar esta anotación")
            
        await annotation.delete()
        return True
    
    async def get_annotation_summary(
        self,
        document_id: str
    ) -> Dict[str, Any]:
        """Obtener resumen de anotaciones de un documento.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Dict con estadísticas de anotaciones
        """
        annotations = await self.get_annotations(document_id)
        
        return {
            "total": len(annotations),
            "by_type": {
                "note": len([a for a in annotations if a.type == "note"]),
                "highlight": len([a for a in annotations if a.type == "highlight"]),
                "comment": len([a for a in annotations if a.type == "comment"])
            },
            "by_page": {
                page: len([a for a in annotations if a.position["page"] == page])
                for page in set(a.position["page"] for a in annotations)
            }
        }
