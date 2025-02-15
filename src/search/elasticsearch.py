"""Elasticsearch client and utilities."""
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from src.config import settings

class ElasticsearchClient:
    """Client for interacting with Elasticsearch."""
    
    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client = Elasticsearch(
            [settings.ES_URL],
            basic_auth=(settings.ES_USER, settings.ES_PASSWORD),
            verify_certs=settings.ES_VERIFY_CERTS
        )
        
        # Índices
        self.document_index = "documents"
        self.annotation_index = "annotations"
        
    def create_indices(self):
        """Create necessary indices if they don't exist."""
        # Índice de documentos
        if not self.client.indices.exists(index=self.document_index):
            self.client.indices.create(
                index=self.document_index,
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    },
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "content": {"type": "text"},
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"},
                            "user_id": {"type": "keyword"},
                            "permissions": {"type": "object"}
                        }
                    }
                }
            )
            
        # Índice de anotaciones
        if not self.client.indices.exists(index=self.annotation_index):
            self.client.indices.create(
                index=self.annotation_index,
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    },
                    "mappings": {
                        "properties": {
                            "document_id": {"type": "keyword"},
                            "user_id": {"type": "keyword"},
                            "content": {"type": "text"},
                            "position": {"type": "object"},
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"}
                        }
                    }
                }
            )
    
    def index_document(self, document: Dict[str, Any]):
        """Index a document."""
        return self.client.index(
            index=self.document_index,
            id=document['id'],
            document=document
        )
    
    def index_annotation(self, annotation: Dict[str, Any]):
        """Index an annotation."""
        return self.client.index(
            index=self.annotation_index,
            id=annotation['id'],
            document=annotation
        )
    
    def bulk_index_documents(self, documents: List[Dict[str, Any]]):
        """Bulk index multiple documents."""
        actions = [
            {
                "_index": self.document_index,
                "_id": doc['id'],
                "_source": doc
            }
            for doc in documents
        ]
        return bulk(self.client, actions)
    
    def search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None,
                        from_: int = 0, size: int = 10) -> Dict[str, Any]:
        """Search for documents."""
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "content", "metadata.*"]
                            }
                        }
                    ]
                }
            },
            "from": from_,
            "size": size,
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {}
                }
            }
        }
        
        if filters:
            body["query"]["bool"]["filter"] = [
                {"term": {k: v}} for k, v in filters.items()
            ]
            
        return self.client.search(
            index=self.document_index,
            body=body
        )
    
    def search_annotations(self, document_id: str, query: Optional[str] = None,
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Search for annotations in a document."""
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"document_id": document_id}}
                    ]
                }
            },
            "sort": [
                {"created_at": {"order": "desc"}}
            ]
        }
        
        if query:
            body["query"]["bool"]["must"].append({
                "match": {"content": query}
            })
            
        if user_id:
            body["query"]["bool"]["must"].append({
                "term": {"user_id": user_id}
            })
            
        return self.client.search(
            index=self.annotation_index,
            body=body
        )
    
    def delete_document(self, document_id: str):
        """Delete a document and its annotations."""
        # Eliminar documento
        self.client.delete(
            index=self.document_index,
            id=document_id
        )
        
        # Eliminar anotaciones asociadas
        self.client.delete_by_query(
            index=self.annotation_index,
            body={
                "query": {
                    "term": {
                        "document_id": document_id
                    }
                }
            }
        )
