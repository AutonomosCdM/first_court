"""Configuration module for the API."""
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """API settings."""
    
    model_config = {
        "env_file": None,
        "case_sensitive": True,
        "extra": "forbid",
        "validate_default": True,
        "use_enum_values": True
    }
    # JWT Settings
    JWT_SECRET: str = Field(default="dev-secret-do-not-use-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=8)
    
    # Monitoring Settings
    PROMETHEUS_PORT: int = Field(default=9090)
    GRAFANA_PORT: int = Field(default=3000)
    
    # Google Integration Settings
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_CALENDAR_ID: str = Field(default="primary")
    GOOGLE_DRIVE_FOLDER_ID: str = Field(default="")
    GOOGLE_AUTH_URI: str = Field(default="https://accounts.google.com/o/oauth2/auth")
    GOOGLE_TOKEN_URI: str = Field(default="https://oauth2.googleapis.com/token")
    GOOGLE_AUTH_PROVIDER_CERT_URL: str = Field(default="https://www.googleapis.com/oauth2/v1/certs")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/oauth2callback")
    
    # Slack Integration Settings
    SLACK_DEFAULT_CHANNEL: str = Field(default="general")
    
    # Database Settings
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/first_court_test")
    DATABASE_POOL_SIZE: int = Field(default=5)
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_PREFIX: str = Field(default="first_court")
    REDIS_MAX_CONNECTIONS: int = Field(default=10)
    
    # Elasticsearch Settings
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200")
    ELASTICSEARCH_INDEX_PREFIX: str = Field(default="first_court")
    ELASTICSEARCH_USERNAME: str | None = Field(default=None)
    ELASTICSEARCH_PASSWORD: str | None = Field(default=None)
    
    # App Settings
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="DEBUG")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


