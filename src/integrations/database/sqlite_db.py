import sqlite3
from typing import Any, Dict, Optional, List
from contextlib import contextmanager

from src.core.database.base import BaseDatabase

class SQLiteDatabase(BaseDatabase):
    """SQLite database implementation"""
    
    def __init__(self, db_path: str):
        """Initialize SQLite database
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def connect(self) -> None:
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None
    
    def begin_transaction(self) -> None:
        """Begin a database transaction"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        self.conn.execute("BEGIN TRANSACTION")
    
    def commit_transaction(self) -> None:
        """Commit the current transaction"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        self.conn.commit()
    
    def rollback_transaction(self) -> None:
        """Rollback the current transaction"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        self.conn.rollback()
    
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a database query
        
        Args:
            query (str): SQL query to execute
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            Query results
        """
        if not self.cursor:
            raise RuntimeError("Database not connected")
        
        if params:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)
    
    def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database
        
        Args:
            query (str): SQL query to execute
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            Optional[Dict[str, Any]]: Row data or None if no results
        """
        self.execute(query, params)
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from the database
        
        Args:
            query (str): SQL query to execute
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            List[Dict[str, Any]]: List of row data
        """
        self.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    @contextmanager
    def connection(self):
        """Context manager for database connection"""
        self.connect()
        try:
            yield self
        finally:
            self.disconnect()
