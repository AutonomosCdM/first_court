from prometheus_client import Counter, Histogram, Gauge
from typing import Dict
import time

# Métricas para endpoints REST
canvas_api_requests = Counter(
    'canvas_api_requests_total',
    'Total de requests a la API del canvas',
    ['endpoint', 'method', 'status']
)

canvas_api_latency = Histogram(
    'canvas_api_latency_seconds',
    'Latencia de requests a la API del canvas',
    ['endpoint'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Métricas para WebSocket
canvas_ws_connections = Gauge(
    'canvas_ws_connections',
    'Conexiones WebSocket activas por caso',
    ['case_id']
)

canvas_ws_messages = Counter(
    'canvas_ws_messages_total',
    'Total de mensajes WebSocket',
    ['case_id', 'event_type']
)

# Métricas de canvas
canvas_nodes = Gauge(
    'canvas_nodes_total',
    'Total de nodos por caso',
    ['case_id']
)

canvas_edges = Gauge(
    'canvas_edges_total',
    'Total de conexiones por caso',
    ['case_id']
)

class CanvasMetrics:
    @staticmethod
    async def track_api_request(endpoint: str, method: str, status: int):
        """Registra una request a la API"""
        canvas_api_requests.labels(
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()

    @staticmethod
    def track_api_latency(endpoint: str):
        """Decorador para medir latencia de endpoints"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    canvas_api_latency.labels(
                        endpoint=endpoint
                    ).observe(duration)
            return wrapper
        return decorator

    @staticmethod
    def track_ws_connection(case_id: str, connected: bool):
        """Registra conexión/desconexión WebSocket"""
        if connected:
            canvas_ws_connections.labels(case_id=case_id).inc()
        else:
            canvas_ws_connections.labels(case_id=case_id).dec()

    @staticmethod
    def track_ws_message(case_id: str, event_type: str):
        """Registra mensaje WebSocket"""
        canvas_ws_messages.labels(
            case_id=case_id,
            event_type=event_type
        ).inc()

    @staticmethod
    async def update_canvas_metrics(case_id: str, nodes: int, edges: int):
        """Actualiza métricas del canvas"""
        canvas_nodes.labels(case_id=case_id).set(nodes)
        canvas_edges.labels(case_id=case_id).set(edges)
