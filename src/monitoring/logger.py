"""Logging configuration and utilities."""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler
from src.config import settings

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        output = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }
        
        if hasattr(record, 'request_id'):
            output['request_id'] = record.request_id
            
        if hasattr(record, 'user_id'):
            output['user_id'] = record.user_id
            
        if record.exc_info:
            output['exception'] = self.formatException(record.exc_info)
            
        if hasattr(record, 'extra'):
            output.update(record.extra)
            
        return json.dumps(output)

def setup_logging(
    level: str = 'INFO',
    log_dir: Optional[Path] = None,
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """Setup application logging.
    
    Args:
        level: Logging level
        log_dir: Directory for log files
        max_size: Maximum size of each log file
        backup_count: Number of backup files to keep
    """
    # Crear directorio de logs si no existe
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpiar handlers existentes
    root_logger.handlers = []
    
    # Formatter JSON
    json_formatter = JsonFormatter()
    
    # Handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)
    
    if log_dir:
        # Handler de archivo para todos los logs
        file_handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=max_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)
        
        # Handler específico para errores
        error_handler = RotatingFileHandler(
            log_dir / 'error.log',
            maxBytes=max_size,
            backupCount=backup_count
        )
        error_handler.setFormatter(json_formatter)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)

class Logger:
    """Logger wrapper with context."""
    
    def __init__(self, name: str):
        """Initialize logger with name."""
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def with_context(self, **kwargs) -> 'Logger':
        """Add context to logger."""
        self.context.update(kwargs)
        return self
    
    def _log(self, level: int, msg: str, *args, **kwargs):
        """Internal logging method."""
        if self.context:
            extra = kwargs.get('extra', {})
            extra.update(self.context)
            kwargs['extra'] = extra
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log info message."""
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, msg, *args, **kwargs)
