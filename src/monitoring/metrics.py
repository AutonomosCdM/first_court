"""Metrics collection and reporting."""
from typing import Dict, Any, Optional, List
import time
from datetime import datetime
from dataclasses import dataclass, field
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, push_to_gateway
from src.config import settings

@dataclass
class MetricsManager:
    """Manager for application metrics."""
    
    registry: CollectorRegistry = field(default_factory=CollectorRegistry)
    
    # Contadores
    http_requests: Counter = field(init=False)
    ws_connections: Counter = field(init=False)
    document_operations: Counter = field(init=False)
    search_queries: Counter = field(init=False)
    errors: Counter = field(init=False)
    
    # Histogramas
    request_duration: Histogram = field(init=False)
    document_size: Histogram = field(init=False)
    search_latency: Histogram = field(init=False)
    
    # Gauges
    active_users: Gauge = field(init=False)
    active_documents: Gauge = field(init=False)
    storage_usage: Gauge = field(init=False)
    
    def __post_init__(self):
        """Initialize metrics."""
        # Contadores
        self.http_requests = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.ws_connections = Counter(
            'ws_connections_total',
            'Total WebSocket connections',
            ['document_id'],
            registry=self.registry
        )
        
        self.document_operations = Counter(
            'document_operations_total',
            'Total document operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.search_queries = Counter(
            'search_queries_total',
            'Total search queries',
            ['type'],
            registry=self.registry
        )
        
        self.errors = Counter(
            'errors_total',
            'Total errors',
            ['type', 'component'],
            registry=self.registry
        )
        
        # Histogramas
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['endpoint'],
            registry=self.registry
        )
        
        self.document_size = Histogram(
            'document_size_bytes',
            'Document size in bytes',
            ['type'],
            registry=self.registry
        )
        
        self.search_latency = Histogram(
            'search_latency_seconds',
            'Search query latency in seconds',
            ['type'],
            registry=self.registry
        )
        
        # Gauges
        self.active_users = Gauge(
            'active_users',
            'Number of active users',
            registry=self.registry
        )
        
        self.active_documents = Gauge(
            'active_documents',
            'Number of active documents',
            registry=self.registry
        )
        
        self.storage_usage = Gauge(
            'storage_usage_bytes',
            'Storage usage in bytes',
            ['type'],
            registry=self.registry
        )
    
    def track_request(self, method: str, endpoint: str, status: int,
                     duration: float):
        """Track HTTP request."""
        self.http_requests.labels(method=method, endpoint=endpoint,
                                status=status).inc()
        self.request_duration.labels(endpoint=endpoint).observe(duration)
    
    def track_ws_connection(self, document_id: str):
        """Track WebSocket connection."""
        self.ws_connections.labels(document_id=document_id).inc()
    
    def track_document_operation(self, operation: str, status: str = 'success'):
        """Track document operation."""
        self.document_operations.labels(
            operation=operation,
            status=status
        ).inc()
    
    def track_search_query(self, query_type: str, duration: float):
        """Track search query."""
        self.search_queries.labels(type=query_type).inc()
        self.search_latency.labels(type=query_type).observe(duration)
    
    def track_error(self, error_type: str, component: str):
        """Track error."""
        self.errors.labels(type=error_type, component=component).inc()
    
    def update_active_users(self, count: int):
        """Update active users gauge."""
        self.active_users.set(count)
    
    def update_active_documents(self, count: int):
        """Update active documents gauge."""
        self.active_documents.set(count)
    
    def update_storage_usage(self, usage: int, storage_type: str):
        """Update storage usage gauge."""
        self.storage_usage.labels(type=storage_type).set(usage)
    
    def push_metrics(self):
        """Push metrics to Prometheus gateway."""
        if settings.PROMETHEUS_GATEWAY:
            try:
                push_to_gateway(
                    settings.PROMETHEUS_GATEWAY,
                    job='first_court',
                    registry=self.registry
                )
            except Exception as e:
                print(f"Error pushing metrics: {e}")

# Instancia global
metrics = MetricsManager()
