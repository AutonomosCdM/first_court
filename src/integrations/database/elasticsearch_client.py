"""
Cliente de Elasticsearch para búsqueda de documentos
"""
import logging
from typing import Dict, List, Optional
from elasticsearch import Elasticsearch
from elasticsearch import ApiError as ElasticsearchException

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(
        self,
        hosts: List[str] = None,
        index_prefix: str = "first_court"
    ):
        """
        Inicializar cliente de Elasticsearch
        
        Args:
            hosts: Lista de hosts de Elasticsearch
            index_prefix: Prefijo para los índices
        """
        self.hosts = hosts or ["http://localhost:9200"]
        self.index_prefix = index_prefix
        self.client = Elasticsearch(self.hosts)
        
    def create_indices(self):
        """Crear índices necesarios"""
        indices = {
            "cases": {
                "mappings": {
                    "properties": {
                        "case_number": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "spanish"
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "spanish"
                        },
                        "status": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            },
            "documents": {
                "mappings": {
                    "properties": {
                        "case_id": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "spanish"
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "spanish"
                        },
                        "document_type": {"type": "keyword"},
                        "created_at": {"type": "date"}
                    }
                }
            }
        }
        
        for name, body in indices.items():
            index_name = f"{self.index_prefix}_{name}"
            try:
                if not self.client.indices.exists(index=index_name):
                    self.client.indices.create(
                        index=index_name,
                        body=body
                    )
                    logger.info(f"Índice creado: {index_name}")
            except ElasticsearchException as e:
                logger.error(f"Error al crear índice {index_name}: {e}")
                raise
                
    def index_document(
        self,
        doc_type: str,
        document: Dict,
        doc_id: Optional[str] = None
    ) -> Dict:
        """
        Indexar un documento
        
        Args:
            doc_type: Tipo de documento (cases, documents)
            document: Documento a indexar
            doc_id: ID del documento (opcional)
        """
        index_name = f"{self.index_prefix}_{doc_type}"
        try:
            response = self.client.index(
                index=index_name,
                id=doc_id,
                document=document
            )
            logger.info(f"Documento indexado: {doc_id}")
            return response
            
        except ElasticsearchException as e:
            logger.error(f"Error al indexar documento: {e}")
            raise
            
    def search_documents(
        self,
        query: str,
        doc_type: str,
        filters: Optional[Dict] = None,
        highlight_fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Buscar documentos
        
        Args:
            query: Consulta de búsqueda
            doc_type: Tipo de documento (cases, documents)
            filters: Filtros adicionales
        """
        index_name = f"{self.index_prefix}_{doc_type}"
        
        # Construir query
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "content", "description"],
                                "analyzer": "spanish"
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    field: {} for field in (highlight_fields or ["title", "content", "description"])
                }
            }
        }
        
        # Agregar filtros si existen
        if filters:
            search_body["query"]["bool"]["filter"] = [
                {"term": {k: v}} for k, v in filters.items()
            ]
            
        try:
            response = self.client.search(
                index=index_name,
                body=search_body
            )
            logger.info(f"Búsqueda realizada: {query}")
            return response
            
        except ElasticsearchException as e:
            logger.error(f"Error en búsqueda: {e}")
            raise
