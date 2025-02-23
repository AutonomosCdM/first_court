import pytest
import os
import sqlite3
from datetime import datetime
from typing import Generator

from src.integrations.database.sqlite_db import SQLiteDatabase

@pytest.fixture
def test_db_path(tmp_path) -> Generator[str, None, None]:
    """Fixture to create a temporary database path"""
    db_path = str(tmp_path / "test.db")
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def db(test_db_path) -> Generator[SQLiteDatabase, None, None]:
    """Fixture to create a test database instance"""
    database = SQLiteDatabase(test_db_path)
    yield database
    database.disconnect()

def test_connection(db: SQLiteDatabase, test_db_path: str):
    """Test database connection and disconnection"""
    # Test connection
    db.connect()
    assert db.conn is not None
    assert db.cursor is not None
    assert os.path.exists(test_db_path)
    
    # Test disconnection
    db.disconnect()
    assert db.conn is None
    assert db.cursor is None

def test_transaction_commit(db: SQLiteDatabase):
    """Test transaction commit"""
    with db.connection():
        # Create test table
        db.execute('''
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Test transaction commit
        with db.transaction():
            db.execute(
                "INSERT INTO test (value) VALUES (:value)",
                {"value": "test data"}
            )
        
        # Verify data was committed
        result = db.fetch_one("SELECT value FROM test WHERE id = 1")
        assert result is not None
        assert result["value"] == "test data"

def test_transaction_rollback(db: SQLiteDatabase):
    """Test transaction rollback"""
    with db.connection():
        # Create test table
        db.execute('''
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Test transaction rollback
        try:
            with db.transaction():
                db.execute(
                    "INSERT INTO test (value) VALUES (:value)",
                    {"value": "test data"}
                )
                raise Exception("Test rollback")
        except Exception:
            pass
        
        # Verify data was rolled back
        result = db.fetch_one("SELECT value FROM test WHERE id = 1")
        assert result is None

def test_fetch_operations(db: SQLiteDatabase):
    """Test fetch operations"""
    with db.connection():
        # Create test table
        db.execute('''
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Insert test data
        test_data = ["value1", "value2", "value3"]
        for value in test_data:
            db.execute(
                "INSERT INTO test (value) VALUES (:value)",
                {"value": value}
            )
        
        # Test fetch_one
        result = db.fetch_one(
            "SELECT value FROM test WHERE id = :id",
            {"id": 1}
        )
        assert result is not None
        assert result["value"] == "value1"
        
        # Test fetch_all
        results = db.fetch_all("SELECT value FROM test ORDER BY id")
        assert len(results) == 3
        assert [r["value"] for r in results] == test_data

def test_connection_context_manager(db: SQLiteDatabase):
    """Test connection context manager"""
    with db.connection():
        assert db.conn is not None
        assert db.cursor is not None
        
        # Execute test query
        db.execute('''
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        ''')
    
    # Verify connection is closed after context
    assert db.conn is None
    assert db.cursor is None

def test_error_handling(db: SQLiteDatabase):
    """Test error handling"""
    # Test executing without connection
    with pytest.raises(RuntimeError, match="Database not connected"):
        db.execute("SELECT 1")
    
    # Test invalid SQL
    with db.connection():
        with pytest.raises(sqlite3.OperationalError):
            db.execute("INVALID SQL")
