"""API routes for document management."""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.documents.template_manager import TemplateManager
from src.auth.auth_manager import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Models
class TemplateCreate(BaseModel):
    """Model for creating a template."""
    template_type: str
    title: str
    content: str

class DocumentCreate(BaseModel):
    """Model for creating a document from template."""
    template_id: str
    variables: Dict[str, Any]

class DocumentPermission(BaseModel):
    """Model for document permissions."""
    email: str
    role: str = "reader"

# Routes
@router.get("/templates")
async def list_templates(
    template_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List available templates."""
    template_manager = TemplateManager()
    return template_manager.list_templates(template_type)

@router.post("/templates")
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new template."""
    template_manager = TemplateManager()
    return template_manager.create_template(
        template_type=template.template_type,
        title=template.title,
        content=template.content
    )

@router.post("/create")
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a document from template."""
    template_manager = TemplateManager()
    return template_manager.create_from_template(
        template_id=document.template_id,
        variables=document.variables
    )

@router.post("/{document_id}/permissions")
async def set_document_permission(
    document_id: str,
    permission: DocumentPermission,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Set permissions for a document."""
    template_manager = TemplateManager()
    template_manager.drive_client.set_permissions(
        file_id=document_id,
        email=permission.email,
        role=permission.role
    )
    return {"status": "success", "message": "Permission updated"}
