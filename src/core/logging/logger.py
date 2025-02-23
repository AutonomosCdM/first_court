import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler

class Logger:
    """Centralized logging configuration"""
    
    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """Initialize logger
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Minimum log level
            max_bytes: Maximum size of each log file
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper())
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Setup handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configure logging handlers"""
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler for all logs
        main_log_file = os.path.join(
            self.log_dir,
            f"{self.name.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = RotatingFileHandler(
            main_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(file_handler)
        
        # File handler for errors only
        error_log_file = os.path.join(
            self.log_dir,
            f"{self.name.lower()}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        )
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(error_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)
    
    def _get_formatter(self) -> logging.Formatter:
        """Get log formatter
        
        Returns:
            Configured log formatter
        """
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_logger(self) -> logging.Logger:
        """Get configured logger
        
        Returns:
            Configured logging.Logger instance
        """
        return self.logger
    
    def set_level(self, level: str):
        """Set log level
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = getattr(logging, level.upper())
        self.logger.setLevel(self.log_level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(self.log_level)
    
    def add_file_handler(
        self,
        filename: str,
        level: str = "INFO",
        formatter: Optional[logging.Formatter] = None
    ):
        """Add additional file handler
        
        Args:
            filename: Log file name
            level: Log level for this handler
            formatter: Optional custom formatter
        """
        handler = RotatingFileHandler(
            os.path.join(self.log_dir, filename),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        handler.setLevel(getattr(logging, level.upper()))
        handler.setFormatter(formatter or self._get_formatter())
        self.logger.addHandler(handler)
    
    def log_with_context(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log message with additional context
        
        Args:
            level: Log level
            message: Log message
            context: Optional context dictionary
        """
        log_method = getattr(self.logger, level.lower())
        if context:
            message = f"{message} - Context: {context}"
        log_method(message)
    
    def cleanup_old_logs(self, days: int = 30):
        """Remove log files older than specified days
        
        Args:
            days: Number of days to keep logs
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        for file in Path(self.log_dir).glob("*.log*"):
            if file.stat().st_mtime < cutoff:
                file.unlink()
