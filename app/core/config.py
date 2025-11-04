from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class Settings(BaseModel):
    model_config = ConfigDict(
        title="Resume Parser Settings",
        validate_assignment=True,
        frozen=True,
        env_file=".env"
    )
    
    PROJECT_NAME: str = "AI-Powered Resume Parser"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/resume_parser"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # In production, use secure key
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Model Settings
    LLM_MODEL: str = "gpt-3.5-turbo"  # OpenAI model
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = ["pdf", "docx", "txt", "jpg", "png"]
    
    # Performance
    WORKERS_COUNT: int = 4
    CACHE_TTL: int = 3600  # 1 hour
    
settings = Settings()