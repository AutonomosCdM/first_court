import os
import pytest
from typing import Generator
from pathlib import Path

from src.core.config.settings import Settings, SlackConfig, DatabaseConfig

@pytest.fixture
def env_file(tmp_path) -> Generator[Path, None, None]:
    """Create a temporary .env file for testing"""
    env_content = """
    ENV=testing
    SECRETARY_SLACK_APP_ID=A12345
    SECRETARY_BOT_TOKEN=xoxb-test-token
    SECRETARY_SIGNING_SECRET=test-secret
    JUDGE_SLACK_APP_ID=B67890
    JUDGE_BOT_TOKEN=xoxb-judge-token
    JUDGE_SIGNING_SECRET=judge-secret
    PROSECUTOR_SLACK_APP_ID=C11223
    PROSECUTOR_BOT_TOKEN=xoxb-prosecutor-token
    PROSECUTOR_SIGNING_SECRET=prosecutor-secret
    DEFENDER_SLACK_APP_ID=D44556
    DEFENDER_BOT_TOKEN=xoxb-defender-token
    DEFENDER_SIGNING_SECRET=defender-secret
    SLACK_GENERAL_CHANNEL=C12345
    SLACK_NOTIFICATIONS_CHANNEL=C67890
    SLACK_ADMIN_USERS=U12345,U67890
    DEFAULT_WORKSPACE=T12345
    DEFAULT_LOCALE=es_CL
    DEFAULT_TIMEZONE=America/Santiago
    SLACK_DB_PATH=/tmp/test.db
    """
    
    env_file = tmp_path / ".env.test"
    env_file.write_text(env_content)
    yield env_file
    env_file.unlink()

def test_load_settings(env_file: Path):
    """Test loading settings from environment file"""
    settings = Settings.load(str(env_file))
    
    # Test environment
    assert settings.env == "testing"
    
    # Test Slack configuration
    assert settings.slack.secretary_app_id == "A12345"
    assert settings.slack.secretary_bot_token == "xoxb-test-token"
    assert settings.slack.secretary_signing_secret == "test-secret"
    assert settings.slack.general_channel == "C12345"
    assert settings.slack.notifications_channel == "C67890"
    assert settings.slack.admin_users == ["U12345", "U67890"]
    assert settings.slack.default_workspace == "T12345"
    assert settings.slack.default_locale == "es_CL"
    assert settings.slack.default_timezone == "America/Santiago"
    
    # Test database configuration
    assert settings.database.slack_db_path == "/tmp/test.db"

def test_settings_validation_success(env_file: Path):
    """Test settings validation with valid configuration"""
    settings = Settings.load(str(env_file))
    errors = settings.validate()
    assert len(errors) == 0

def test_settings_validation_failure():
    """Test settings validation with missing required fields"""
    # Create settings with empty values
    slack_config = SlackConfig(
        secretary_app_id="",
        secretary_bot_token="",
        secretary_signing_secret="",
        judge_app_id="",
        judge_bot_token="",
        judge_signing_secret="",
        prosecutor_app_id="",
        prosecutor_bot_token="",
        prosecutor_signing_secret="",
        defender_app_id="",
        defender_bot_token="",
        defender_signing_secret="",
        general_channel="",
        notifications_channel="",
        admin_users=[],
        default_workspace="",
        default_locale="es_CL",
        default_timezone="America/Santiago"
    )
    
    settings = Settings(
        env="development",
        slack=slack_config,
        database=DatabaseConfig()
    )
    
    errors = settings.validate()
    
    # Check for required field errors
    assert len(errors) > 0
    assert "SECRETARY_SLACK_APP_ID is required" in errors
    assert "SECRETARY_BOT_TOKEN is required" in errors
    assert "SECRETARY_SIGNING_SECRET is required" in errors
    assert "SLACK_GENERAL_CHANNEL is required" in errors
    assert "SLACK_NOTIFICATIONS_CHANNEL is required" in errors
    assert "DEFAULT_WORKSPACE is required" in errors

def test_settings_as_dict(env_file: Path):
    """Test converting settings to dictionary"""
    settings = Settings.load(str(env_file))
    settings_dict = settings.as_dict()
    
    assert settings_dict["env"] == "testing"
    assert settings_dict["slack"]["secretary_app_id"] == "A12345"
    assert settings_dict["slack"]["general_channel"] == "C12345"
    assert settings_dict["database"]["slack_db_path"] == "/tmp/test.db"

def test_default_values():
    """Test default values when environment variables are not set"""
    settings = Settings.load()
    
    assert settings.env == "development"
    assert settings.slack.default_locale == "es_CL"
    assert settings.slack.default_timezone == "America/Santiago"
    assert settings.database.slack_db_path == "db/slack_integration.sqlite"

def test_multiple_env_files(tmp_path: Path):
    """Test loading from multiple environment files"""
    # Create .env file
    (tmp_path / ".env").write_text("ENV=production\n")
    
    # Create .env.local file with override
    (tmp_path / ".env.local").write_text("ENV=local\n")
    
    # Change working directory temporarily
    original_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    
    try:
        settings = Settings.load()
        assert settings.env == "local"  # Should use .env.local over .env
    finally:
        os.chdir(original_cwd)
