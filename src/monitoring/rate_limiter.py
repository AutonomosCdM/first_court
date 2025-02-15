"""Rate limiter para APIs."""
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class TokenBucket:
    """Implementación de Token Bucket para rate limiting."""
    
    capacity: int
    fill_rate: float
    tokens: float = 0.0
    last_update: datetime = datetime.utcnow()
    
    def update(self):
        """Actualizar tokens basado en tiempo transcurrido."""
        now = datetime.utcnow()
        delta = (now - self.last_update).total_seconds()
        self.tokens = min(
            self.capacity,
            self.tokens + delta * self.fill_rate
        )
        self.last_update = now
    
    def try_consume(self, tokens: int = 1) -> bool:
        """Intentar consumir tokens."""
        self.update()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class RateLimiter:
    """Rate limiter con soporte para múltiples recursos."""
    
    def __init__(
        self,
        rate: int,
        period: int = 60,
        burst: Optional[int] = None
    ):
        """Inicializar rate limiter.
        
        Args:
            rate: Número de requests permitidos
            period: Período en segundos
            burst: Tamaño del burst (opcional)
        """
        self.rate = rate
        self.period = period
        self.burst = burst or rate
        
        self.bucket = TokenBucket(
            capacity=self.burst,
            fill_rate=self.rate / self.period
        )
        
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1):
        """Adquirir tokens, esperando si es necesario."""
        async with self._lock:
            while not self.bucket.try_consume(tokens):
                # Calcular tiempo de espera
                required = tokens - self.bucket.tokens
                wait_time = required / self.bucket.fill_rate
                
                logger.debug(
                    f"Rate limit alcanzado. Esperando {wait_time:.2f}s "
                    f"para {tokens} tokens"
                )
                
                # Esperar con jitter para evitar thundering herd
                jitter = wait_time * 0.1  # 10% jitter
                wait_time += jitter * (asyncio.random() - 0.5)
                
                await asyncio.sleep(wait_time)
    
    async def __aenter__(self):
        """Entrar al contexto del rate limiter."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Salir del contexto del rate limiter."""
        pass

class ResourceRateLimiter:
    """Rate limiter para múltiples recursos."""
    
    def __init__(self, default_config: Dict[str, Dict[str, int]]):
        """Inicializar rate limiter.
        
        Args:
            default_config: Configuración por defecto para recursos
                {
                    "resource_name": {
                        "rate": requests_per_period,
                        "period": seconds,
                        "burst": max_burst
                    }
                }
        """
        self.limiters: Dict[str, RateLimiter] = {}
        self.default_config = default_config
    
    def get_limiter(self, resource: str) -> RateLimiter:
        """Obtener o crear rate limiter para un recurso."""
        if resource not in self.limiters:
            config = self.default_config.get(resource, {
                "rate": 1000,
                "period": 60,
                "burst": None
            })
            
            self.limiters[resource] = RateLimiter(
                rate=config["rate"],
                period=config["period"],
                burst=config.get("burst")
            )
        
        return self.limiters[resource]
    
    async def acquire(self, resource: str, tokens: int = 1):
        """Adquirir tokens para un recurso específico."""
        limiter = self.get_limiter(resource)
        await limiter.acquire(tokens)
    
    def context(self, resource: str, tokens: int = 1):
        """Obtener contexto para un recurso específico."""
        return self.get_limiter(resource).__aenter__()
