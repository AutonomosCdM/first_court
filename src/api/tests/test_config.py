"""Test configuration module."""
import pytest
from api.config import Settings

def test_settings_default_values():
    """Test default values for settings."""
    settings = Settings(
        DATABASE_POOL_SIZE=5,
        REDIS_MAX_CONNECTIONS=10,
        JWT_SECRET="dev-secret-do-not-use-in-production",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRATION_HOURS=8,
        PROMETHEUS_PORT=9090,
        GRAFANA_PORT=3000,
        GOOGLE_CLIENT_ID="",
        GOOGLE_CLIENT_SECRET="",
        GOOGLE_CALENDAR_ID="primary",
        GOOGLE_DRIVE_FOLDER_ID="",
        GOOGLE_AUTH_URI="https://accounts.google.com/o/oauth2/auth",
        GOOGLE_TOKEN_URI="https://oauth2.googleapis.com/token",
        GOOGLE_AUTH_PROVIDER_CERT_URL="https://www.googleapis.com/oauth2/v1/certs",
        GOOGLE_REDIRECT_URI="http://localhost:8000/oauth2callback",
        SLACK_DEFAULT_CHANNEL="general",
        DATABASE_URL="postgresql://postgres:postgres@localhost:5432/first_court_test",
        REDIS_URL="redis://localhost:6379/0",
        REDIS_PREFIX="first_court",
        ELASTICSEARCH_URL="http://localhost:9200",
        ELASTICSEARCH_INDEX_PREFIX="first_court",
        ELASTICSEARCH_USERNAME=None,
        ELASTICSEARCH_PASSWORD=None,
        DEBUG=True,
        ENVIRONMENT="development",
        LOG_LEVEL="DEBUG"
    )
    
    # JWT Settings
    assert settings.JWT_SECRET == "dev-secret-do-not-use-in-production"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.JWT_EXPIRATION_HOURS == 8
    
    # Monitoring
    assert settings.PROMETHEUS_PORT == 9090
    assert settings.GRAFANA_PORT == 3000
    
    # Database
    assert settings.DATABASE_POOL_SIZE == 5
    assert settings.DATABASE_URL == "postgresql://postgres:postgres@localhost:5432/first_court_test"
    
    # Redis
    assert settings.REDIS_MAX_CONNECTIONS == 10
    assert settings.REDIS_PREFIX == "first_court"
    
    # App Settings
    assert settings.DEBUG is True
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "DEBUG"

def test_settings_override():
    """Test overriding settings values."""
    test_values = {
        "JWT_SECRET": "override-secret",
        "DATABASE_POOL_SIZE": 10,
        "DEBUG": True,
        "REDIS_MAX_CONNECTIONS": 10,
        "JWT_ALGORITHM": "HS256",
        "JWT_EXPIRATION_HOURS": 8,
        "PROMETHEUS_PORT": 9090,
        "GRAFANA_PORT": 3000,
        "GOOGLE_CLIENT_ID": "",
        "GOOGLE_CLIENT_SECRET": "",
        "GOOGLE_CALENDAR_ID": "primary",
        "GOOGLE_DRIVE_FOLDER_ID": "",
        "GOOGLE_AUTH_URI": "https://accounts.google.com/o/oauth2/auth",
        "GOOGLE_TOKEN_URI": "https://oauth2.googleapis.com/token",
        "GOOGLE_AUTH_PROVIDER_CERT_URL": "https://www.googleapis.com/oauth2/v1/certs",
        "GOOGLE_REDIRECT_URI": "http://localhost:8000/oauth2callback",
        "SLACK_DEFAULT_CHANNEL": "general",
        "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/first_court_test",
        "REDIS_URL": "redis://localhost:6379/0",
        "REDIS_PREFIX": "first_court",
        "ELASTICSEARCH_URL": "http://localhost:9200",
        "ELASTICSEARCH_INDEX_PREFIX": "first_court",
        "ELASTICSEARCH_USERNAME": None,
        "ELASTICSEARCH_PASSWORD": None,
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG"
    }
    
    settings = Settings(**test_values)
    
    assert settings.JWT_SECRET == "override-secret"
    assert settings.DATABASE_POOL_SIZE == 10
    assert settings.DEBUG is True
