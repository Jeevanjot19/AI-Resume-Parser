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
        case_sensitive=True
    )
    
    # Project Info
    PROJECT_NAME: str = "AI-Powered Resume Parser"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "resume_parser"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @property
    def sync_database_url(self) -> str:
        return str(self.DATABASE_URL).replace("+asyncpg", "")
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[RedisDsn] = None
    
    # Elasticsearch
    ELASTICSEARCH_HOST: str = "elasticsearch"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_URL: Optional[HttpUrl] = None
    
    # Security
    SECRET_KEY: SecretStr = Field(default="your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # AI/ML Settings
    LLM_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    SPACY_MODEL: str = "en_core_web_trf"
    MODEL_CACHE_DIR: str = "/app/models"
    
    # Document Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "jpg", "png"]
    UPLOAD_DIR: str = "/app/uploads"
    OCR_LANG: str = "eng"
    TIKA_SERVER_JAR: str = "/usr/local/bin/tika-server.jar"
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    
    # Celery
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
    def get_database_url(self) -> PostgresDsn:
        """Constructs database URL from components."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=int(self.POSTGRES_PORT),
                path=f"/{self.POSTGRES_DB}"
            )
        return self.DATABASE_URL
    
    def get_redis_url(self) -> RedisDsn:
        """Constructs Redis URL from components."""
        if not self.REDIS_URL:
            self.REDIS_URL = RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT
            )
        return self.REDIS_URL
    
    def get_elasticsearch_url(self) -> HttpUrl:
        """Constructs Elasticsearch URL from components."""
        if not self.ELASTICSEARCH_URL:
            self.ELASTICSEARCH_URL = HttpUrl.build(
                scheme="http",
                host=self.ELASTICSEARCH_HOST,
                port=self.ELASTICSEARCH_PORT
            )
        return self.ELASTICSEARCH_URL

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Creates a cached instance of settings."""
    return Settings()

settings = get_settings()