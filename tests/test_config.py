import pytest
from app.core.config import settings

def test_settings_defaults():
    """Test default settings values"""
    assert settings.PROJECT_NAME == "AI-Powered Resume Parser"
    assert settings.API_V1_STR == "/api/v1"
    assert isinstance(settings.MAX_FILE_SIZE, int)
    assert settings.MAX_FILE_SIZE == 10 * 1024 * 1024  # 10MB
    assert isinstance(settings.ALLOWED_FILE_TYPES, list)
    assert "pdf" in settings.ALLOWED_FILE_TYPES
    assert "docx" in settings.ALLOWED_FILE_TYPES

def test_database_url():
    """Test database URL configuration"""
    assert settings.DATABASE_URL.startswith("postgresql://")

def test_redis_url():
    """Test Redis URL configuration"""
    assert settings.REDIS_URL.startswith("redis://")

def test_security_settings():
    """Test security-related settings"""
    assert settings.SECRET_KEY is not None
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0

def test_ai_model_settings():
    """Test AI model configuration"""
    assert settings.LLM_MODEL is not None
    assert settings.EMBEDDING_MODEL is not None

def test_performance_settings():
    """Test performance-related settings"""
    assert isinstance(settings.WORKERS_COUNT, int)
    assert settings.WORKERS_COUNT > 0
    assert isinstance(settings.CACHE_TTL, int)
    assert settings.CACHE_TTL > 0