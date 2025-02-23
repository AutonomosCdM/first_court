import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

@dataclass
class SlackConfig:
    """Slack-specific configuration"""
    secretary_app_id: str
    secretary_bot_token: str
    secretary_signing_secret: str
    judge_app_id: str
    judge_bot_token: str
    judge_signing_secret: str
    prosecutor_app_id: str
    prosecutor_bot_token: str
    prosecutor_signing_secret: str
    defender_app_id: str
    defender_bot_token: str
    defender_signing_secret: str
    general_channel: str
    notifications_channel: str
    admin_users: list[str]
    default_workspace: str
    default_locale: str
    default_timezone: str

@dataclass
class DatabaseConfig:
    """Database configuration"""
    slack_db_path: str = "db/slack_integration.sqlite"

@dataclass
class Settings:
    """Global application settings"""
    env: str
    slack: SlackConfig
    database: DatabaseConfig
    
    @classmethod
    def load(cls, env_file: Optional[str] = None) -> 'Settings':
        """Load settings from environment variables
        
        Args:
            env_file: Optional path to .env file
            
        Returns:
            Settings instance
        """
        # Load environment variables
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            # Try default locations
            env_paths = [
                ".env",
                ".env.local",
                f".env.{os.getenv('ENV', 'development')}",
            ]
            for path in env_paths:
                if os.path.exists(path):
                    load_dotenv(path)
                    break
        
        # Load Slack configuration
        slack_config = SlackConfig(
            secretary_app_id=os.getenv("SECRETARY_SLACK_APP_ID", ""),
            secretary_bot_token=os.getenv("SECRETARY_BOT_TOKEN", ""),
            secretary_signing_secret=os.getenv("SECRETARY_SIGNING_SECRET", ""),
            judge_app_id=os.getenv("JUDGE_SLACK_APP_ID", ""),
            judge_bot_token=os.getenv("JUDGE_BOT_TOKEN", ""),
            judge_signing_secret=os.getenv("JUDGE_SIGNING_SECRET", ""),
            prosecutor_app_id=os.getenv("PROSECUTOR_SLACK_APP_ID", ""),
            prosecutor_bot_token=os.getenv("PROSECUTOR_BOT_TOKEN", ""),
            prosecutor_signing_secret=os.getenv("PROSECUTOR_SIGNING_SECRET", ""),
            defender_app_id=os.getenv("DEFENDER_SLACK_APP_ID", ""),
            defender_bot_token=os.getenv("DEFENDER_BOT_TOKEN", ""),
            defender_signing_secret=os.getenv("DEFENDER_SIGNING_SECRET", ""),
            general_channel=os.getenv("SLACK_GENERAL_CHANNEL", ""),
            notifications_channel=os.getenv("SLACK_NOTIFICATIONS_CHANNEL", ""),
            admin_users=os.getenv("SLACK_ADMIN_USERS", "").split(","),
            default_workspace=os.getenv("DEFAULT_WORKSPACE", ""),
            default_locale=os.getenv("DEFAULT_LOCALE", "es_CL"),
            default_timezone=os.getenv("DEFAULT_TIMEZONE", "America/Santiago")
        )
        
        # Load database configuration
        database_config = DatabaseConfig(
            slack_db_path=os.getenv("SLACK_DB_PATH", "db/slack_integration.sqlite")
        )
        
        return cls(
            env=os.getenv("ENV", "development"),
            slack=slack_config,
            database=database_config
        )
    
    def validate(self) -> list[str]:
        """Validate settings
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate Slack settings
        if not self.slack.secretary_app_id:
            errors.append("SECRETARY_SLACK_APP_ID is required")
        if not self.slack.secretary_bot_token:
            errors.append("SECRETARY_BOT_TOKEN is required")
        if not self.slack.secretary_signing_secret:
            errors.append("SECRETARY_SIGNING_SECRET is required")
        
        # Validate required channels
        if not self.slack.general_channel:
            errors.append("SLACK_GENERAL_CHANNEL is required")
        if not self.slack.notifications_channel:
            errors.append("SLACK_NOTIFICATIONS_CHANNEL is required")
        
        # Validate workspace
        if not self.slack.default_workspace:
            errors.append("DEFAULT_WORKSPACE is required")
        
        return errors
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary
        
        Returns:
            Dictionary of settings
        """
        return {
            "env": self.env,
            "slack": {
                "secretary_app_id": self.slack.secretary_app_id,
                "general_channel": self.slack.general_channel,
                "notifications_channel": self.slack.notifications_channel,
                "admin_users": self.slack.admin_users,
                "default_workspace": self.slack.default_workspace,
                "default_locale": self.slack.default_locale,
                "default_timezone": self.slack.default_timezone
            },
            "database": {
                "slack_db_path": self.database.slack_db_path
            }
        }
