from typing import Optional, Dict, Any

class AgentCourtError(Exception):
    """Base exception for all AgentCourt errors"""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error
        
        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def __str__(self) -> str:
        """String representation of error"""
        if self.details:
            return f"{self.code}: {self.message} - Details: {self.details}"
        return f"{self.code}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary
        
        Returns:
            Dictionary representation of error
        """
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }

class ConfigurationError(AgentCourtError):
    """Error related to configuration issues"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "CONFIGURATION_ERROR", details)

class DatabaseError(AgentCourtError):
    """Error related to database operations"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "DATABASE_ERROR", details)

class ValidationError(AgentCourtError):
    """Error related to data validation"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "VALIDATION_ERROR", details)

class IntegrationError(AgentCourtError):
    """Error related to external integrations"""
    
    def __init__(
        self,
        message: str,
        service: str,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["service"] = service
        super().__init__(message, "INTEGRATION_ERROR", details)

class AuthenticationError(AgentCourtError):
    """Error related to authentication"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AUTHENTICATION_ERROR", details)

class AuthorizationError(AgentCourtError):
    """Error related to authorization"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AUTHORIZATION_ERROR", details)

class AgentError(AgentCourtError):
    """Error related to agent operations"""
    
    def __init__(
        self,
        message: str,
        agent_type: str,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["agent_type"] = agent_type
        super().__init__(message, "AGENT_ERROR", details)

class CaseError(AgentCourtError):
    """Error related to case operations"""
    
    def __init__(
        self,
        message: str,
        case_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["case_id"] = case_id
        super().__init__(message, "CASE_ERROR", details)
