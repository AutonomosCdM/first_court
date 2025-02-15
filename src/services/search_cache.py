"""
Servicio de caché para búsquedas frecuentes.
Implementa un sistema de caché con TTL y LRU para optimizar búsquedas.
"""
from typing import Dict, List, Optional
import json
import hashlib
from datetime import datetime, timedelta
import redis
from src.config import settings
from src.monitoring.logger import Logger
from src.monitoring.metrics import search_metrics

logger = Logger(__name__)

class SearchCache:
    def __init__(self):
        """Inicializar servicio de caché."""
        self.redis = redis.Redis.from_url(settings.REDIS_URL)
        self.config = {
            'default_ttl': 3600,  # 1 hora
            'min_frequency': 3,   # Mínimo de búsquedas para cachear
            'max_results': 1000,  # Máximo de resultados por query
            'max_size': 10_000    # Máximo de queries en caché
        }

    async def get_cached_results(
        self,
        query: str,
        document_id: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Obtener resultados cacheados para una búsqueda.
        
        Args:
            query: Texto de búsqueda
            document_id: ID opcional del documento
            options: Opciones de búsqueda
            
        Returns:
            Resultados cacheados o None si no existe
        """
        try:
            with search_metrics.measure_latency("cache_get"):
                cache_key = self._generate_cache_key(query, document_id, options)
                
                # Obtener datos de caché
                cached = self.redis.get(cache_key)
                if not cached:
                    return None
                
                # Actualizar estadísticas
                self._update_stats(cache_key, hit=True)
                
                return json.loads(cached)
                
        except Exception as e:
            logger.error(f"Error getting cached results: {str(e)}")
            return None

    async def cache_results(
        self,
        query: str,
        results: Dict,
        document_id: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> bool:
        """Cachear resultados de búsqueda.
        
        Args:
            query: Texto de búsqueda
            results: Resultados a cachear
            document_id: ID opcional del documento
            options: Opciones de búsqueda
            
        Returns:
            True si se cacheó correctamente
        """
        try:
            with search_metrics.measure_latency("cache_set"):
                cache_key = self._generate_cache_key(query, document_id, options)
                
                # Verificar si debemos cachear
                if not self._should_cache(cache_key, results):
                    return False
                
                # Cachear resultados
                self.redis.setex(
                    cache_key,
                    self.config['default_ttl'],
                    json.dumps(results)
                )
                
                # Actualizar estadísticas
                self._update_stats(cache_key, hit=False)
                
                return True
                
        except Exception as e:
            logger.error(f"Error caching results: {str(e)}")
            return False

    async def invalidate_cache(
        self,
        document_id: Optional[str] = None,
        query: Optional[str] = None
    ):
        """Invalidar caché de búsqueda.
        
        Args:
            document_id: ID opcional del documento para invalidar
            query: Query opcional para invalidar
        """
        try:
            with search_metrics.measure_latency("cache_invalidate"):
                pattern = "search:"
                if document_id:
                    pattern += f"{document_id}:"
                if query:
                    pattern += self._hash_query(query)
                pattern += "*"
                
                # Obtener keys que coinciden con el patrón
                keys = self.redis.keys(pattern)
                
                # Eliminar keys
                if keys:
                    self.redis.delete(*keys)
                    
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")

    async def get_stats(self) -> Dict:
        """Obtener estadísticas del caché."""
        try:
            stats_key = "search_cache:stats"
            stats = self.redis.hgetall(stats_key)
            
            return {
                "total_queries": int(stats.get(b"total_queries", 0)),
                "cache_hits": int(stats.get(b"cache_hits", 0)),
                "cache_misses": int(stats.get(b"cache_misses", 0)),
                "cached_queries": len(self.redis.keys("search:*"))
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}

    def _generate_cache_key(
        self,
        query: str,
        document_id: Optional[str],
        options: Optional[Dict]
    ) -> str:
        """Generar key de caché para una búsqueda."""
        key_parts = ["search"]
        
        if document_id:
            key_parts.append(document_id)
            
        key_parts.append(self._hash_query(query))
        
        if options:
            key_parts.append(self._hash_query(json.dumps(options, sort_keys=True)))
            
        return ":".join(key_parts)

    def _hash_query(self, query: str) -> str:
        """Generar hash de query para usar como key."""
        return hashlib.md5(query.encode()).hexdigest()

    def _should_cache(self, cache_key: str, results: Dict) -> bool:
        """Determinar si se debe cachear una búsqueda."""
        # Verificar tamaño de resultados
        if len(results.get("results", [])) > self.config['max_results']:
            return False
            
        # Verificar frecuencia de búsqueda
        stats_key = f"{cache_key}:stats"
        frequency = int(self.redis.get(stats_key) or 0)
        
        return frequency >= self.config['min_frequency']

    def _update_stats(self, cache_key: str, hit: bool):
        """Actualizar estadísticas de caché."""
        stats_key = "search_cache:stats"
        query_stats_key = f"{cache_key}:stats"
        
        pipeline = self.redis.pipeline()
        
        # Actualizar estadísticas globales
        pipeline.hincrby(stats_key, "total_queries", 1)
        if hit:
            pipeline.hincrby(stats_key, "cache_hits", 1)
        else:
            pipeline.hincrby(stats_key, "cache_misses", 1)
            
        # Actualizar frecuencia de query
        pipeline.incr(query_stats_key)
        pipeline.expire(query_stats_key, self.config['default_ttl'])
        
        pipeline.execute()
