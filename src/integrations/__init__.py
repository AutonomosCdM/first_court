"""
External Integrations Module.
Handles integration with external services like Slack, Firebase, etc.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseIntegration(ABC):
    """Base class for external service integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize integration.
        
        Args:
            config: Integration configuration
        """
        self.config = config
        self._client = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to external service.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to external service."""
        pass
        
    @property
    def client(self):
        """Get service client instance."""
        if not self._client:
            raise RuntimeError("Integration not connected")
        return self._client
        
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check integration health/connectivity.
        
        Returns:
            True if healthy, False otherwise
        """
        pass

class IntegrationError(Exception):
    """Base exception for integration errors."""
    
    def __init__(self, message: str, service: str, details: Optional[Dict] = None):
        """
        Initialize integration error.
        
        Args:
            message: Error message
            service: Name of service that raised error
            details: Optional error details
        """
        self.service = service
        self.details = details or {}
        super().__init__(f"{service} integration error: {message}")

class IntegrationConnectionError(IntegrationError):
    """Raised when connection to service fails."""
    pass

class IntegrationAuthError(IntegrationError):
    """Raised when authentication with service fails."""
    pass

class IntegrationTimeoutError(IntegrationError):
    """Raised when service request times out."""
    pass
