"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # App
    APP_NAME: str = "Car Dealership API"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database (using existing PostgreSQL)
    DATABASE_URL: str = "postgresql+asyncpg://ula@localhost:5432/postgres"
    DATABASE_URL_SYNC: str = "postgresql://ula@localhost:5432/postgres"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Business settings
    DEFAULT_MARKUP_PERCENT: float = 12.0
    DEFAULT_BLACKLIST_THRESHOLD: int = 3
    
    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_DOCUMENT_TYPES: list = ["application/pdf"]
    ALLOWED_VIDEO_TYPES: list = ["video/mp4", "video/quicktime", "video/x-msvideo"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
