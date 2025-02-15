"""
Middleware de optimización para la aplicación.
Implementa compresión, caché y optimización de respuestas.
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import gzip
import json
from typing import Dict, List
import redis
from src.config import settings
from src.monitoring.logger import Logger
from src.monitoring.metrics import optimization_metrics

logger = Logger(__name__)
redis_client = redis.Redis.from_url(settings.REDIS_URL)

class OptimizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Configuración de caché
        self.cache_config = {
            "default_ttl": 300,  # 5 minutos
            "max_size": 1024 * 1024 * 10  # 10MB
        }
        # Rutas cacheables
        self.cacheable_paths = [
            r"/api/documents/\d+$",
            r"/api/documents/\d+/annotations$"
        ]
        
    async def dispatch(self, request: Request, call_next):
        try:
            # 1. Intentar obtener de caché
            cached_response = await self._get_from_cache(request)
            if cached_response:
                return await self._compress_response(cached_response)

            # 2. Procesar request
            response = await call_next(request)

            # 3. Cachear si es necesario
            if self._should_cache(request, response):
                await self._cache_response(request, response)

            # 4. Comprimir respuesta
            return await self._compress_response(response)

        except Exception as e:
            logger.error(f"Optimization middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "INTERNAL_SERVER_ERROR"}
            )

    async def _get_from_cache(self, request: Request) -> Response:
        """Obtiene respuesta de caché."""
        with optimization_metrics.measure_latency("cache_get"):
            if not self._is_cacheable(request):
                return None
                
            cache_key = self._get_cache_key(request)
            cached = redis_client.get(cache_key)
            
            if cached:
                data = json.loads(cached)
                return JSONResponse(
                    content=data["content"],
                    status_code=data["status_code"],
                    headers=data["headers"]
                )
            
            return None

    async def _cache_response(self, request: Request, response: Response):
        """Guarda respuesta en caché."""
        with optimization_metrics.measure_latency("cache_set"):
            if not self._should_cache(request, response):
                return
                
            cache_key = self._get_cache_key(request)
            
            # Preparar datos para caché
            try:
                body = await response.body()
                data = {
                    "content": json.loads(body),
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
                
                # Verificar tamaño
                size = len(json.dumps(data))
                if size <= self.cache_config["max_size"]:
                    redis_client.setex(
                        cache_key,
                        self.cache_config["default_ttl"],
                        json.dumps(data)
                    )
            except Exception as e:
                logger.error(f"Error caching response: {str(e)}")

    async def _compress_response(self, response: Response) -> Response:
        """Comprime la respuesta si es posible."""
        with optimization_metrics.measure_latency("compression"):
            if "gzip" not in response.headers.get("Content-Encoding", ""):
                try:
                    body = await response.body()
                    if len(body) > 1024:  # Comprimir solo si > 1KB
                        compressed = gzip.compress(body)
                        return Response(
                            content=compressed,
                            status_code=response.status_code,
                            headers={
                                **response.headers,
                                "Content-Encoding": "gzip",
                                "Content-Length": str(len(compressed))
                            }
                        )
                except Exception as e:
                    logger.error(f"Error compressing response: {str(e)}")
                    
            return response

    def _is_cacheable(self, request: Request) -> bool:
        """Determina si un request es cacheable."""
        # Solo cachear GETs
        if request.method != "GET":
            return False
            
        # Verificar path
        path = request.url.path
        return any(re.match(pattern, path) for pattern in self.cacheable_paths)

    def _should_cache(self, request: Request, response: Response) -> bool:
        """Determina si una respuesta debe ser cacheada."""
        return (
            self._is_cacheable(request) and
            response.status_code == 200 and
            "no-store" not in response.headers.get("Cache-Control", "")
        )

    def _get_cache_key(self, request: Request) -> str:
        """Genera key de caché para un request."""
        return f"cache:{request.url.path}:{hash(str(request.query_params))}"
