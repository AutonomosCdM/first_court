"""
Common logging configuration for all test modules.
"""
import logging
from pathlib import Path
from datetime import datetime

def setup_test_logging(test_name: str) -> logging.Logger:
    """
    Configure logging for test modules with consistent formatting and output.
    
    Args:
        test_name: Name of the test module for identification
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path('/Users/autonomos_dev/Projects/first_court/tests/logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f"{test_name}_{timestamp}.log"
    
    # Configure logger
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
