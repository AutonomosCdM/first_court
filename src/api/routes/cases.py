"""API routes for case management."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from src.documents.case_manager import CaseManager
from src.auth.auth_manager import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/cases", tags=["cases"])

# Models
class CaseCreate(BaseModel):
    """Model for creating a case structure."""
    case_id: str
    title: str

class DocumentClassify(BaseModel):
    """Model for classifying a document."""
    doc_type: str

# Routes
@router.post("/structure")
async def create_case_structure(
    case: CaseCreate,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create folder structure for a new case."""
    case_manager = CaseManager()
    return case_manager.create_case_structure(
        case_id=case.case_id,
        title=case.title
    )

@router.get("/{case_id}/structure")
async def get_case_structure(
    case_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the complete folder structure of a case."""
    case_manager = CaseManager()
    return case_manager.get_case_structure(case_id)

@router.post("/documents/{file_id}/classify")
async def classify_document(
    file_id: str,
    classification: DocumentClassify,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Classify and move a document to its corresponding folder."""
    case_manager = CaseManager()
    return case_manager.classify_document(
        file_id=file_id,
        doc_type=classification.doc_type
    )

@router.post("/documents/move/{file_id}")
async def move_document(
    file_id: str,
    target_path: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Move a document to a specific folder."""
    case_manager = CaseManager()
    return case_manager.move_to_folder(
        file_id=file_id,
        target_path=target_path
    )
