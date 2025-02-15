"""Search endpoints."""
from typing import Dict, Any, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from src.search.elasticsearch import ElasticsearchClient
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["search"])

@router.get("/search")
async def search_documents(
    q: str = Query(..., description="Search query"),
    document_type: Optional[str] = None,
    user_id: Optional[UUID] = None,
    from_: int = Query(0, alias="from"),
    size: int = Query(10, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Search for documents."""
    es = ElasticsearchClient()
    
    # Construir filtros
    filters = {}
    if document_type:
        filters["metadata.type"] = document_type
    if user_id:
        filters["user_id"] = str(user_id)
        
    # Realizar búsqueda
    results = es.search_documents(
        query=q,
        filters=filters,
        from_=from_,
        size=size
    )
    
    # Formatear resultados
    hits = results["hits"]["hits"]
    total = results["hits"]["total"]["value"]
    
    documents = []
    for hit in hits:
        doc = hit["_source"]
        doc["score"] = hit["_score"]
        if "highlight" in hit:
            doc["highlights"] = hit["highlight"]
        documents.append(doc)
    
    return {
        "total": total,
        "documents": documents,
        "from": from_,
        "size": size
    }

@router.get("/documents/{document_id}/search")
async def search_document_content(
    document_id: UUID,
    q: str = Query(..., description="Search query"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Search within a specific document."""
    es = ElasticsearchClient()
    
    results = es.search_documents(
        query=q,
        filters={"_id": str(document_id)},
        size=1
    )
    
    if not results["hits"]["hits"]:
        return {"matches": []}
        
    # Extraer coincidencias del contenido
    doc = results["hits"]["hits"][0]
    highlights = doc.get("highlight", {})
    
    matches = []
    if "content" in highlights:
        for snippet in highlights["content"]:
            matches.append({
                "text": snippet,
                "score": doc["_score"]
            })
            
    return {"matches": matches}

@router.get("/documents/{document_id}/annotations/search")
async def search_document_annotations(
    document_id: UUID,
    q: Optional[str] = None,
    user_id: Optional[UUID] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Search annotations in a document."""
    es = ElasticsearchClient()
    
    results = es.search_annotations(
        document_id=str(document_id),
        query=q,
        user_id=str(user_id) if user_id else None
    )
    
    annotations = []
    for hit in results["hits"]["hits"]:
        annotation = hit["_source"]
        annotation["score"] = hit["_score"]
        annotations.append(annotation)
    
    return {
        "total": results["hits"]["total"]["value"],
        "annotations": annotations
    }
