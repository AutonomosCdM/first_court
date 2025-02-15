from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "First Court API"
    API_V1_STR: str = "/api"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js default
        "http://localhost:8000",  # Backend default
        "http://localhost",
        "https://firstcourt.dev",  # Production
    ]
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "firstcourt"
    
    # WebSocket
    WS_MESSAGE_QUEUE: str = "redis://localhost"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
