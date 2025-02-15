"""Schemas for document annotations."""
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class AnnotationBase(BaseModel):
    """Base schema for annotations."""
    content: Dict[str, Any] = Field(..., description="Content of the annotation")
    position: Dict[str, Any] = Field(..., description="Position in the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class AnnotationCreate(AnnotationBase):
    """Schema for creating annotations."""
    pass

class AnnotationUpdate(BaseModel):
    """Schema for updating annotations."""
    content: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AnnotationResponse(AnnotationBase):
    """Schema for annotation responses."""
    id: UUID
    document_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True
