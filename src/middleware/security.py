"""
Middleware de seguridad para la aplicación.
Implementa rate limiting, validación de tokens, y protección contra ataques comunes.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import jwt
from typing import Dict, List
import re
import redis
from src.config import settings
from src.monitoring.logger import Logger
from src.monitoring.metrics import security_metrics

logger = Logger(__name__)
redis_client = redis.Redis.from_url(settings.REDIS_URL)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Configuración de rate limiting
        self.rate_limit = {
            "window": 60,  # segundos
            "max_requests": 100  # requests por ventana
        }
        # Patrones de ataques comunes
        self.attack_patterns = [
            r"(?i)(union.*select|drop.*table)",  # SQL Injection
            r"(?i)(<script|javascript:)",         # XSS
            r"(?i)(../|\.\.\\)",                 # Path Traversal
        ]
        
    async def dispatch(self, request: Request, call_next):
        try:
            # 1. Rate Limiting
            if not await self._check_rate_limit(request):
                logger.warning(f"Rate limit exceeded for IP: {request.client.host}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "RATE_LIMIT_EXCEEDED"}
                )

            # 2. Validación de Token
            if not await self._validate_token(request):
                logger.warning("Invalid token detected")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "INVALID_TOKEN"}
                )

            # 3. Sanitización y Validación
            if not await self._validate_request(request):
                logger.warning("Potential attack detected in request")
                return JSONResponse(
                    status_code=400,
                    content={"detail": "INVALID_REQUEST"}
                )

            # 4. Headers de Seguridad
            response = await call_next(request)
            return await self._add_security_headers(response)

        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "INTERNAL_SERVER_ERROR"}
            )

    async def _check_rate_limit(self, request: Request) -> bool:
        """Implementa rate limiting basado en IP."""
        with security_metrics.measure_latency("rate_limit_check"):
            ip = request.client.host
            key = f"rate_limit:{ip}"
            
            # Obtener contador actual
            current = redis_client.get(key)
            
            if current is None:
                # Primer request en la ventana
                redis_client.setex(
                    key,
                    self.rate_limit["window"],
                    1
                )
                return True
            
            current = int(current)
            if current >= self.rate_limit["max_requests"]:
                return False
            
            # Incrementar contador
            redis_client.incr(key)
            return True

    async def _validate_token(self, request: Request) -> bool:
        """Valida el token JWT."""
        with security_metrics.measure_latency("token_validation"):
            # Ignorar rutas públicas
            if request.url.path in settings.PUBLIC_PATHS:
                return True
                
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return False
                
            token = auth.split(" ")[1]
            try:
                jwt.decode(
                    token,
                    settings.JWT_SECRET,
                    algorithms=["HS256"]
                )
                return True
            except jwt.InvalidTokenError:
                return False

    async def _validate_request(self, request: Request) -> bool:
        """Valida el request contra patrones de ataque."""
        with security_metrics.measure_latency("request_validation"):
            # Obtener body si existe
            body = await request.body()
            body_str = body.decode() if body else ""
            
            # Obtener query params
            query = str(request.query_params)
            
            # Contenido a validar
            content = f"{request.url.path} {query} {body_str}"
            
            # Verificar patrones de ataque
            for pattern in self.attack_patterns:
                if re.search(pattern, content):
                    return False
            
            return True

    async def _add_security_headers(self, response):
        """Añade headers de seguridad a la respuesta."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
