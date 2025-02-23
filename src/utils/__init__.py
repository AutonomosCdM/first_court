"""
Utilities Module.
Common utilities and helper functions used across the application.
"""

import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a logger with given name and level.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

class JsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling dates and custom objects."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)

def load_json(path: Path) -> Dict[str, Any]:
    """
    Load JSON file.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If invalid JSON
    """
    with open(path) as f:
        return json.load(f)

def save_json(data: Dict[str, Any], path: Path) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        path: Output file path
    """
    with open(path, 'w') as f:
        json.dump(data, f, cls=JsonEncoder, indent=2)

class Singleton(type):
    """Metaclass for implementing singleton pattern."""
    
    _instances: Dict = {}
    
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

def chunks(lst: List, n: int) -> List[List]:
    """
    Split list into chunks of size n.
    
    Args:
        lst: List to split
        n: Chunk size
        
    Returns:
        List of chunks
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    return "".join(c for c in filename if c.isalnum() or c in "._- ")
