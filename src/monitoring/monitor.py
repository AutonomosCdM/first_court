"""Centralized monitoring system for First Court.
Handles logging, metrics, and system health checks.
"""
from typing import Dict, Any, List
import psutil
import os
import time
from datetime import datetime
from pathlib import Path
from src.monitoring.logger import Logger
from src.monitoring.metrics import metrics

logger = Logger(__name__)

class SystemMonitor:
    """Monitor system resources and health."""
    
    def __init__(self):
        """Initialize system monitor."""
        self.start_time = time.time()
        self.project_root = Path('/Users/autonomos_dev/Projects/first_court')
        self.logs_dir = self.project_root / 'logs'
        self.metrics_dir = self.project_root / 'metrics'
        
        # Crear directorios si no existen
        self.logs_dir.mkdir(exist_ok=True)
        self.metrics_dir.mkdir(exist_ok=True)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics.update_storage_usage(disk.used, 'system')
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'uptime': time.time() - self.start_time
        }
    
    def get_process_metrics(self) -> Dict[str, Any]:
        """Get current process metrics."""
        process = psutil.Process(os.getpid())
        
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_info': process.memory_info()._asdict(),
            'open_files': len(process.open_files()),
            'threads': process.num_threads(),
            'connections': len(process.connections())
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health."""
        try:
            system_metrics = self.get_system_metrics()
            process_metrics = self.get_process_metrics()
            
            # Verificar umbrales
            warnings = []
            
            if system_metrics['cpu']['percent'] > 80:
                warnings.append('High CPU usage')
                
            if system_metrics['memory']['percent'] > 80:
                warnings.append('High memory usage')
                
            if system_metrics['disk']['percent'] > 80:
                warnings.append('Low disk space')
            
            status = 'healthy' if not warnings else 'warning'
            
            return {
                'status': status,
                'timestamp': datetime.utcnow().isoformat(),
                'warnings': warnings,
                'metrics': {
                    'system': system_metrics,
                    'process': process_metrics
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            metrics.track_error('health_check', 'monitor')
            
            return {
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def get_service_status(self) -> Dict[str, str]:
        """Get status of dependent services."""
        services = {
            'redis': self._check_redis(),
            'elasticsearch': self._check_elasticsearch(),
            's3': self._check_s3()
        }
        
        return services
    
    def _check_redis(self) -> str:
        """Check Redis connection."""
        from src.database import get_redis
        try:
            redis = get_redis()
            redis.ping()
            return 'healthy'
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return 'error'
    
    def _check_elasticsearch(self) -> str:
        """Check Elasticsearch connection."""
        from src.search.elasticsearch import ElasticsearchClient
        try:
            es = ElasticsearchClient()
            es.client.ping()
            return 'healthy'
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return 'error'
    
    def _check_s3(self) -> str:
        """Check S3 connection."""
        from src.storage.s3 import S3Client
        try:
            s3 = S3Client()
            s3.client.list_buckets()
            return 'healthy'
        except Exception as e:
            logger.error(f"S3 health check failed: {e}")
            return 'error'

# Instancia global
monitor = SystemMonitor()
