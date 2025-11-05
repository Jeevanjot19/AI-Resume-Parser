import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, PostgresDsn, RedisDsn, HttpUrl, SecretStr
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    model_config = ConfigDict(
        title="Resume Parser Settings",
        validate_assignment=True,
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from .env
    )
    
    # Project Info
    PROJECT_NAME: str = "AI-Powered Resume Parser"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database (supports both PostgreSQL and SQLite)
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "resume_parser"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None  # Changed to accept both PostgreSQL and SQLite URLs
    
    @property
    def sync_database_url(self) -> str:
        """Returns synchronous database URL."""
        if self.DATABASE_URL:
            # Handle both PostgreSQL and SQLite URLs
            db_url = str(self.DATABASE_URL)
            if "postgresql" in db_url:
                return db_url.replace("+asyncpg", "")
            return db_url  # SQLite URLs remain unchanged
        return "sqlite:///./data/resume_parser.db"  # Default to SQLite
    
    # Redis (Optional for local development)
    REDIS_ENABLED: bool = True  # Can be disabled for local setup
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None
    
    # Elasticsearch (Optional for local development)
    ELASTICSEARCH_ENABLED: bool = True  # Can be disabled for local setup
    ELASTICSEARCH_HOST: str = "elasticsearch"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: SecretStr = Field(default="your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # AI/ML Settings
    LLM_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    SPACY_MODEL: str = "en_core_web_lg"  # Using large model instead of transformer (no C++ compiler needed)
    MODEL_CACHE_DIR: str = "./models"  # Changed to relative path for local setup
    USE_GPU: bool = False  # Disabled by default for local setup
    
    # Document Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "jpg", "png"]
    UPLOAD_DIR: str = "./data/uploads"  # Changed to relative path for local setup
    OCR_LANG: str = "eng"
    TIKA_SERVER_JAR: str = "/usr/local/bin/tika-server.jar"
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    
    # Celery (Optional for local development)
    CELERY_ENABLED: bool = True  # Can be disabled for local setup
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Performance & Scaling
    WORKERS_COUNT: int = 4
    CACHE_TTL: int = 3600  # 1 hour
    MAX_CONNECTIONS_COUNT: int = 100
    MIN_CONNECTIONS_COUNT: int = 10
    
    # Monitoring
    SENTRY_DSN: Optional[HttpUrl] = None
    METRICS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    LOGGING_CONFIG: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json"
            }
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO"
        }
    }
    
    # Model class methods
    def get_database_url(self) -> str:
        """Constructs database URL from components."""
        if not self.DATABASE_URL:
            # Check if we should use SQLite (local) or PostgreSQL (Docker)
            if self.POSTGRES_SERVER == "postgres":
                # Docker environment - use PostgreSQL
                self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            else:
                # Local environment - use SQLite
                self.DATABASE_URL = "sqlite:///./data/resume_parser.db"
        return self.DATABASE_URL
    
    def get_redis_url(self) -> str:
        """Constructs Redis URL from components."""
        if not self.REDIS_URL and self.REDIS_ENABLED:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
        return self.REDIS_URL or ""
    
    def get_elasticsearch_url(self) -> str:
        """Constructs Elasticsearch URL from components."""
        if not self.ELASTICSEARCH_URL and self.ELASTICSEARCH_ENABLED:
            self.ELASTICSEARCH_URL = f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"
        return self.ELASTICSEARCH_URL or ""


@lru_cache()
def get_settings() -> Settings:
    """Creates a cached instance of settings."""
    return Settings()

settings = get_settings()