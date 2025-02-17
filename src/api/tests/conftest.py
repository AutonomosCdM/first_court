import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import asyncio
from typing import Generator
from unittest.mock import patch

from api.config import Settings
from api.middleware.auth import AuthHandler

@pytest.fixture(scope="session")
def auth_handler(test_settings) -> AuthHandler:
    """Create auth handler with test settings and configure global instance."""
    from api.middleware.auth import auth_handler as global_handler
    
    # Crear nueva instancia
    handler = AuthHandler.__new__(AuthHandler)
    handler.settings = test_settings
    handler.secret = test_settings.JWT_SECRET
    
    # Configurar instancia global
    global_handler = handler
    
    return handler

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        DATABASE_POOL_SIZE=5,
        REDIS_MAX_CONNECTIONS=10,
        JWT_SECRET="test-secret",
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

@pytest.fixture(autouse=True)
def mock_settings(test_settings: Settings):
    """Mock get_settings to return test settings."""
    with patch("api.config.get_settings", return_value=test_settings):
        yield test_settings

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Create a FastAPI app instance for testing."""
    from ..main import app
    return app

@pytest.fixture(scope="session")
def client(app: FastAPI) -> Generator:
    """Create a TestClient instance."""
    with TestClient(app) as client:
        yield client
