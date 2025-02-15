from fastapi import APIRouter, HTTPException, WebSocket, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from app.models.document import Document, DocumentPage, DocumentThumbnail
from app.services.document_service import DocumentService
from app.core.auth import get_current_user
from app.core.websocket import ConnectionManager

router = APIRouter(prefix="/api/documents", tags=["documents"])
manager = ConnectionManager()

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user = Depends(get_current_user)
) -> Document:
    try:
        document = await DocumentService.get_document(document_id, current_user)
        return document
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/thumbnails/{page}")
async def get_thumbnail(
    document_id: str,
    page: int,
    current_user = Depends(get_current_user)
) -> DocumentThumbnail:
    try:
        thumbnail = await DocumentService.get_thumbnail(document_id, page, current_user)
        return thumbnail
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.websocket("/{document_id}/collaboration")
async def websocket_endpoint(
    websocket: WebSocket,
    document_id: str
):
    await manager.connect(websocket, document_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast to all connected clients for this document
            await manager.broadcast(document_id, data)
    except Exception as e:
        await manager.disconnect(websocket, document_id)
