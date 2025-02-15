"""Service for managing document annotations."""
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.models.annotations import Annotation

class AnnotationService:
    """Service for managing document annotations."""
    
    def __init__(self, db_session: Session):
        """Initialize the annotation service."""
        self.db = db_session
    
    def create_annotation(self, data: Dict[str, Any]) -> Annotation:
        """Create a new annotation."""
        annotation = Annotation.from_dict(data)
        self.db.add(annotation)
        self.db.commit()
        self.db.refresh(annotation)
        return annotation
    
    def get_annotation(self, annotation_id: UUID) -> Optional[Annotation]:
        """Get an annotation by ID."""
        return self.db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    def get_document_annotations(self, document_id: UUID) -> List[Annotation]:
        """Get all annotations for a document."""
        return self.db.query(Annotation).filter(
            Annotation.document_id == document_id
        ).order_by(Annotation.created_at.desc()).all()
    
    def update_annotation(self, annotation_id: UUID, data: Dict[str, Any]) -> Optional[Annotation]:
        """Update an annotation."""
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return None
            
        for key, value in data.items():
            if hasattr(annotation, key):
                setattr(annotation, key, value)
                
        self.db.commit()
        self.db.refresh(annotation)
        return annotation
    
    def delete_annotation(self, annotation_id: UUID) -> bool:
        """Delete an annotation."""
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return False
            
        self.db.delete(annotation)
        self.db.commit()
        return True
    
    def get_user_annotations(self, user_id: UUID, document_id: Optional[UUID] = None) -> List[Annotation]:
        """Get all annotations by a user, optionally filtered by document."""
        query = self.db.query(Annotation).filter(Annotation.user_id == user_id)
        if document_id:
            query = query.filter(Annotation.document_id == document_id)
        return query.order_by(Annotation.created_at.desc()).all()
