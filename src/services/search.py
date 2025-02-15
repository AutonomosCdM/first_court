"""
Servicio de búsqueda con caché integrado.
"""
from typing import Dict, List, Optional
from elasticsearch import AsyncElasticsearch
from src.config import settings
from src.monitoring.logger import Logger
from src.monitoring.metrics import search_metrics
from src.services.search_cache import SearchCache

logger = Logger(__name__)

class SearchService:
    def __init__(self):
        """Inicializar servicio de búsqueda."""
        self.es = AsyncElasticsearch([settings.ES_URL])
        self.cache = SearchCache()
        
    async def search_document(
        self,
        document_id: str,
        query: str,
        options: Optional[Dict] = None,
        user = None
    ) -> Dict:
        """Buscar en un documento.
        
        Args:
            document_id: ID del documento
            query: Texto a buscar
            options: Opciones de búsqueda
            user: Usuario que realiza la búsqueda
            
        Returns:
            Resultados de búsqueda
        """
        try:
            with search_metrics.measure_latency("document_search"):
                # 1. Intentar obtener de caché
                cached = await self.cache.get_cached_results(
                    query=query,
                    document_id=document_id,
                    options=options
                )
                
                if cached:
                    logger.info(f"Cache hit for query: {query}")
                    return cached
                
                # 2. Realizar búsqueda en Elasticsearch
                search_body = self._build_search_query(query, options)
                
                results = await self.es.search(
                    index=f"documents_{document_id}",
                    body=search_body,
                    _source=["text", "pageNumber", "position"]
                )
                
                # 3. Formatear resultados
                formatted_results = self._format_results(results)
                
                # 4. Cachear resultados
                await self.cache.cache_results(
                    query=query,
                    results=formatted_results,
                    document_id=document_id,
                    options=options
                )
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error searching document: {str(e)}")
            raise

    async def invalidate_document_cache(self, document_id: str):
        """Invalidar caché de un documento.
        
        Args:
            document_id: ID del documento
        """
        try:
            await self.cache.invalidate_cache(document_id=document_id)
        except Exception as e:
            logger.error(f"Error invalidating document cache: {str(e)}")

    async def get_search_stats(self) -> Dict:
        """Obtener estadísticas de búsqueda."""
        try:
            return await self.cache.get_stats()
        except Exception as e:
            logger.error(f"Error getting search stats: {str(e)}")
            return {}

    def _build_search_query(self, query: str, options: Optional[Dict] = None) -> Dict:
        """Construir query de Elasticsearch.
        
        Args:
            query: Texto a buscar
            options: Opciones de búsqueda
            
        Returns:
            Query de Elasticsearch
        """
        # Opciones por defecto
        opts = {
            "caseSensitive": False,
            "wholeWord": False,
            "useRegex": False,
            **(options or {})
        }
        
        # Base de la query
        search_query = {
            "bool": {
                "must": []
            }
        }
        
        # Agregar condiciones según opciones
        if opts["useRegex"]:
            search_query["bool"]["must"].append({
                "regexp": {
                    "text": {
                        "value": query,
                        "case_insensitive": not opts["caseSensitive"]
                    }
                }
            })
        elif opts["wholeWord"]:
            search_query["bool"]["must"].append({
                "match_phrase": {
                    "text": query
                }
            })
        else:
            search_query["bool"]["must"].append({
                "match": {
                    "text": {
                        "query": query,
                        "operator": "and"
                    }
                }
            })
            
        return {
            "query": search_query,
            "highlight": {
                "fields": {
                    "text": {}
                }
            }
        }

    def _format_results(self, es_results: Dict) -> Dict:
        """Formatear resultados de Elasticsearch.
        
        Args:
            es_results: Resultados de Elasticsearch
            
        Returns:
            Resultados formateados
        """
        hits = es_results.get("hits", {}).get("hits", [])
        
        results = []
        for hit in hits:
            source = hit["_source"]
            highlight = hit.get("highlight", {}).get("text", [""])[0]
            
            results.append({
                "id": hit["_id"],
                "pageNumber": source["pageNumber"],
                "text": source["text"],
                "context": highlight,
                "position": source["position"]
            })
            
        return {
            "results": results,
            "total": es_results["hits"]["total"]["value"]
        }
