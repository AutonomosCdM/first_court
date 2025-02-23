from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from contextlib import contextmanager

class BaseDatabase(ABC):
    """Base interface for all database implementations"""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    def begin_transaction(self) -> None:
        """Begin a database transaction"""
        pass
    
    @abstractmethod
    def commit_transaction(self) -> None:
        """Commit the current transaction"""
        pass
    
    @abstractmethod
    def rollback_transaction(self) -> None:
        """Rollback the current transaction"""
        pass
    
    @contextmanager
    def transaction(self):
        """Context manager for handling transactions"""
        try:
            self.begin_transaction()
            yield
            self.commit_transaction()
        except Exception as e:
            self.rollback_transaction()
            raise e

    @abstractmethod
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a database query
        
        Args:
            query (str): SQL query to execute
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database
        
        Args:
            query (str): SQL query to execute
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            Optional[Dict[str, Any]]: Row data or None if no results
        """
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> list[Dict[str, Any]]:
        """Fetch all rows from the database
        
        Args:
            query (str): SQL query to execute
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            list[Dict[str, Any]]: List of row data
        """
        pass
