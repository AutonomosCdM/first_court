"""Routes for document annotations."""
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.annotations import Annotation
from src.services.annotations import AnnotationService
from src.auth.dependencies import get_current_user
from src.schemas.annotations import (
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse
)

router = APIRouter(prefix="/api/v1/documents", tags=["annotations"])

@router.get("/{document_id}/annotations", response_model=List[AnnotationResponse])
async def get_document_annotations(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all annotations for a document."""
    service = AnnotationService(db)
    annotations = service.get_document_annotations(document_id)
    return [annotation.to_dict() for annotation in annotations]

@router.post("/{document_id}/annotations", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    document_id: UUID,
    annotation: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new annotation."""
    service = AnnotationService(db)
    data = annotation.dict()
    data['document_id'] = str(document_id)
    data['user_id'] = str(current_user['id'])
    
    new_annotation = service.create_annotation(data)
    return new_annotation.to_dict()

@router.put("/{document_id}/annotations/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    document_id: UUID,
    annotation_id: UUID,
    annotation: AnnotationUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update an annotation."""
    service = AnnotationService(db)
    existing = service.get_annotation(annotation_id)
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
        
    if existing.user_id != UUID(current_user['id']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this annotation"
        )
        
    updated = service.update_annotation(annotation_id, annotation.dict(exclude_unset=True))
    return updated.to_dict()

@router.delete("/{document_id}/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    document_id: UUID,
    annotation_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete an annotation."""
    service = AnnotationService(db)
    existing = service.get_annotation(annotation_id)
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found"
        )
        
    if existing.user_id != UUID(current_user['id']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this annotation"
        )
        
    service.delete_annotation(annotation_id)
