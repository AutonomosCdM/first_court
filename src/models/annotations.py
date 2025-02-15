"""Models for document annotations."""
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from .base import Base

class Annotation(Base):
    """Model for document annotations."""
    
    __tablename__ = 'annotations'
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(PostgresUUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content = Column(JSON, nullable=False)  # Contenido de la anotación (texto, dibujo, etc)
    position = Column(JSON, nullable=False)  # Posición en el documento
    metadata = Column(JSON, nullable=True)   # Metadatos adicionales
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    document = relationship("Document", back_populates="annotations")
    user = relationship("User", back_populates="annotations")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert annotation to dictionary."""
        return {
            'id': str(self.id),
            'document_id': str(self.document_id),
            'user_id': str(self.user_id),
            'content': self.content,
            'position': self.position,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        """Create annotation from dictionary."""
        return cls(
            id=UUID(data['id']) if 'id' in data else uuid4(),
            document_id=UUID(data['document_id']),
            user_id=UUID(data['user_id']),
            content=data['content'],
            position=data['position'],
            metadata=data.get('metadata')
        )
