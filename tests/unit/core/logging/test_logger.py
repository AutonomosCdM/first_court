import os
import logging
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator

from src.core.logging.logger import Logger

@pytest.fixture
def log_dir(tmp_path) -> Generator[Path, None, None]:
    """Create a temporary directory for log files"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    yield log_dir
    # Cleanup is handled by pytest's tmp_path

@pytest.fixture
def logger(log_dir) -> Logger:
    """Create a test logger instance"""
    return Logger(
        name="test_logger",
        log_dir=str(log_dir),
        log_level="DEBUG"
    )

def test_logger_initialization(logger: Logger, log_dir: Path):
    """Test logger initialization and basic configuration"""
    # Check logger setup
    assert logger.name == "test_logger"
    assert logger.log_dir == str(log_dir)
    assert logger.log_level == logging.DEBUG
    
    # Check handlers
    python_logger = logger.get_logger()
    assert len(python_logger.handlers) == 3  # File, Error, and Console handlers
    
    # Verify log directory exists
    assert log_dir.exists()

def test_log_file_creation(logger: Logger, log_dir: Path):
    """Test log file creation and naming"""
    today = datetime.now().strftime("%Y%m%d")
    
    # Log some messages
    python_logger = logger.get_logger()
    python_logger.info("Test info message")
    python_logger.error("Test error message")
    
    # Check main log file
    main_log = log_dir / f"test_logger_{today}.log"
    assert main_log.exists()
    content = main_log.read_text()
    assert "Test info message" in content
    assert "Test error message" in content
    
    # Check error log file
    error_log = log_dir / f"test_logger_errors_{today}.log"
    assert error_log.exists()
    content = error_log.read_text()
    assert "Test info message" not in content
    assert "Test error message" in content

def test_log_levels(logger: Logger, log_dir: Path):
    """Test different log levels"""
    python_logger = logger.get_logger()
    
    # Test DEBUG level
    logger.set_level("DEBUG")
    python_logger.debug("Debug message")
    python_logger.info("Info message")
    
    # Test INFO level
    logger.set_level("INFO")
    python_logger.debug("Should not appear")
    python_logger.info("Should appear")
    
    today = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"test_logger_{today}.log"
    content = log_file.read_text()
    
    assert "Debug message" in content
    assert "Info message" in content
    assert "Should not appear" not in content
    assert "Should appear" in content

def test_log_rotation(logger: Logger, log_dir: Path):
    """Test log file rotation"""
    # Configure small max_bytes to test rotation
    logger = Logger(
        name="rotation_test",
        log_dir=str(log_dir),
        max_bytes=50,  # Small size to trigger rotation
        backup_count=2
    )
    
    python_logger = logger.get_logger()
    
    # Generate enough logs to trigger rotation
    for i in range(10):
        python_logger.info(f"Test message {i}" + "x" * 20)
    
    today = datetime.now().strftime("%Y%m%d")
    base_name = f"rotation_test_{today}.log"
    
    # Check that rotation files exist
    assert (log_dir / base_name).exists()
    assert (log_dir / f"{base_name}.1").exists()
    assert (log_dir / f"{base_name}.2").exists()
    assert not (log_dir / f"{base_name}.3").exists()  # Should not exist due to backup_count=2

def test_log_with_context(logger: Logger, log_dir: Path):
    """Test logging with context"""
    context = {"user": "test_user", "action": "login"}
    logger.log_with_context("INFO", "User action", context)
    
    today = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"test_logger_{today}.log"
    content = log_file.read_text()
    
    assert "User action" in content
    assert "Context: {'user': 'test_user', 'action': 'login'}" in content

def test_cleanup_old_logs(logger: Logger, log_dir: Path, monkeypatch):
    """Test cleanup of old log files"""
    # Create some old log files
    old_time = datetime.now() - timedelta(days=40)
    recent_time = datetime.now() - timedelta(days=10)
    
    def create_log_file(name: str, mtime: datetime):
        path = log_dir / name
        path.write_text("test log content")
        os.utime(path, (mtime.timestamp(), mtime.timestamp()))
    
    create_log_file("old_log.log", old_time)
    create_log_file("recent_log.log", recent_time)
    
    # Run cleanup
    logger.cleanup_old_logs(days=30)
    
    # Check results
    assert not (log_dir / "old_log.log").exists()
    assert (log_dir / "recent_log.log").exists()

def test_custom_formatter(logger: Logger, log_dir: Path):
    """Test adding handler with custom formatter"""
    custom_formatter = logging.Formatter('%(levelname)s - %(message)s')
    logger.add_file_handler(
        "custom_format.log",
        level="INFO",
        formatter=custom_formatter
    )
    
    python_logger = logger.get_logger()
    python_logger.info("Test message")
    
    log_file = log_dir / "custom_format.log"
    content = log_file.read_text()
    
    # Should match custom format (no timestamp or logger name)
    assert "INFO - Test message" in content
