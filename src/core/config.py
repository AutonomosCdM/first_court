"""
Core configuration management.
Handles environment variables and configuration across different environments.
"""
import os
from pathlib import Path
from typing import Dict, Any
from functools import lru_cache

from dotenv import load_dotenv

# Environment types
class Environment:
    DEVELOPMENT = "development"
    TESTING = "testing" 
    PRODUCTION = "production"

# Base configuration class
class BaseConfig:
    # Project paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Environment settings
    ENV: str = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    DEBUG: bool = ENV == Environment.DEVELOPMENT
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-secret-key")
    
    # Firebase config
    FIREBASE_CONFIG: Dict[str, Any] = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID")
    }

    # AI Configuration
    AI_MODEL_CONFIG: Dict[str, Any] = {
        "model_name": os.getenv("AI_MODEL_NAME", "gpt-4"),
        "temperature": float(os.getenv("AI_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("AI_MAX_TOKENS", "2000"))
    }

    # Slack Configuration
    SLACK_CONFIG: Dict[str, str] = {
        "token": os.getenv("SLACK_BOT_TOKEN"),
        "signing_secret": os.getenv("SLACK_SIGNING_SECRET"),
        "channel": os.getenv("SLACK_DEFAULT_CHANNEL")
    }

    class Config:
        case_sensitive = True

# Environment specific configurations
class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    class Config:
        env_file = ".env.development"

class TestingConfig(BaseConfig):
    """Testing configuration."""
    ENV = Environment.TESTING
    DEBUG = True

    class Config:
        env_file = ".env.test"

class ProductionConfig(BaseConfig):
    """Production configuration."""
    ENV = Environment.PRODUCTION
    DEBUG = False

    class Config:
        env_file = ".env.production"

# Configuration factory
@lru_cache()
def get_config():
    """
    Factory function to get configuration based on environment.
    Uses LRU cache to avoid reloading environment multiple times.
    """
    env = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    configs = {
        Environment.DEVELOPMENT: DevelopmentConfig,
        Environment.TESTING: TestingConfig,
        Environment.PRODUCTION: ProductionConfig
    }
    
    # Load appropriate .env file
    config_class = configs[env]
    env_file = config_class.Config.env_file
    if os.path.exists(env_file):
        load_dotenv(env_file)
    
    return config_class()

# Global config instance
config = get_config()
