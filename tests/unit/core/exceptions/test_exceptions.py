import pytest
from src.core.exceptions.base import (
    AgentCourtError,
    ConfigurationError,
    DatabaseError,
    ValidationError,
    IntegrationError,
    AuthenticationError,
    AuthorizationError,
    AgentError,
    CaseError
)

def test_base_error():
    """Test base AgentCourtError"""
    error = AgentCourtError("Test error")
    assert str(error) == "INTERNAL_ERROR: Test error"
    
    error_with_details = AgentCourtError(
        "Test error",
        code="TEST_ERROR",
        details={"key": "value"}
    )
    assert str(error_with_details) == "TEST_ERROR: Test error - Details: {'key': 'value'}"
    
    # Test dictionary conversion
    error_dict = error_with_details.to_dict()
    assert error_dict["code"] == "TEST_ERROR"
    assert error_dict["message"] == "Test error"
    assert error_dict["details"] == {"key": "value"}

def test_configuration_error():
    """Test ConfigurationError"""
    error = ConfigurationError(
        "Missing required setting",
        details={"setting": "API_KEY"}
    )
    assert error.code == "CONFIGURATION_ERROR"
    assert "Missing required setting" in str(error)
    assert error.details["setting"] == "API_KEY"

def test_database_error():
    """Test DatabaseError"""
    error = DatabaseError(
        "Connection failed",
        details={"db": "sqlite", "path": "/tmp/test.db"}
    )
    assert error.code == "DATABASE_ERROR"
    assert "Connection failed" in str(error)
    assert error.details["db"] == "sqlite"

def test_validation_error():
    """Test ValidationError"""
    error = ValidationError(
        "Invalid input",
        details={"field": "email", "reason": "invalid format"}
    )
    assert error.code == "VALIDATION_ERROR"
    assert "Invalid input" in str(error)
    assert error.details["field"] == "email"

def test_integration_error():
    """Test IntegrationError"""
    error = IntegrationError(
        "API request failed",
        service="slack",
        details={"status_code": 404}
    )
    assert error.code == "INTEGRATION_ERROR"
    assert "API request failed" in str(error)
    assert error.details["service"] == "slack"
    assert error.details["status_code"] == 404

def test_authentication_error():
    """Test AuthenticationError"""
    error = AuthenticationError(
        "Invalid credentials",
        details={"user": "test_user"}
    )
    assert error.code == "AUTHENTICATION_ERROR"
    assert "Invalid credentials" in str(error)
    assert error.details["user"] == "test_user"

def test_authorization_error():
    """Test AuthorizationError"""
    error = AuthorizationError(
        "Permission denied",
        details={"resource": "case_123", "action": "delete"}
    )
    assert error.code == "AUTHORIZATION_ERROR"
    assert "Permission denied" in str(error)
    assert error.details["resource"] == "case_123"

def test_agent_error():
    """Test AgentError"""
    error = AgentError(
        "Agent initialization failed",
        agent_type="secretary",
        details={"reason": "missing configuration"}
    )
    assert error.code == "AGENT_ERROR"
    assert "Agent initialization failed" in str(error)
    assert error.details["agent_type"] == "secretary"
    assert error.details["reason"] == "missing configuration"

def test_case_error():
    """Test CaseError"""
    error = CaseError(
        "Case not found",
        case_id="2025-001",
        details={"status": "deleted"}
    )
    assert error.code == "CASE_ERROR"
    assert "Case not found" in str(error)
    assert error.details["case_id"] == "2025-001"
    assert error.details["status"] == "deleted"

def test_error_inheritance():
    """Test error class inheritance"""
    errors = [
        ConfigurationError("test"),
        DatabaseError("test"),
        ValidationError("test"),
        IntegrationError("test", "slack"),
        AuthenticationError("test"),
        AuthorizationError("test"),
        AgentError("test", "secretary"),
        CaseError("test", "2025-001")
    ]
    
    for error in errors:
        assert isinstance(error, AgentCourtError)
        assert isinstance(error, Exception)

def test_empty_details():
    """Test errors with no details"""
    error = AgentCourtError("Test error")
    assert error.details == {}
    
    error_dict = error.to_dict()
    assert error_dict["details"] == {}
