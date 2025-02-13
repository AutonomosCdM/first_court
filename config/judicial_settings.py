from pydantic import BaseSettings

class JudicialSettings(BaseSettings):
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    LLM_PROVIDER: str = "deepseek"
    MAX_CONCURRENT_CASES: int = 5
    LEGAL_DB_PATH: str = "./data/legal_db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
