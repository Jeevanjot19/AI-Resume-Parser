"""
FastAPI application main entry point.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from loguru import logger
import sys
from datetime import datetime

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import engine


# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v1.0.0")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1] if settings.DATABASE_URL else 'Not configured'}")
    
    # Log configuration
    logger.info(f"API URL: {settings.API_V1_STR}")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"Tika server: {settings.TIKA_SERVER_URL}")
    logger.info(f"Elasticsearch: {settings.ELASTICSEARCH_URL}")
    logger.info(f"Redis: redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered resume parsing and job matching system with semantic search and analysis",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if hasattr(settings, 'BACKEND_CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": "1.0.0",
        "documentation": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health"
    }


@app.get("/info", tags=["Root"])
async def info():
    """Get API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "api_prefix": settings.API_V1_STR,
        "features": [
            "Multi-format resume parsing (PDF, DOCX, TXT, Images)",
            "AI-powered information extraction (NER, classification)",
            "Semantic search with vector embeddings",
            "Job-resume matching with multi-dimensional scoring",
            "Quality analysis and career path recommendations",
            "Real-time processing with Celery",
            "Comprehensive health checks",
            "Redis caching for performance",
            "Elasticsearch for fast search"
        ],
        "docs": f"{settings.API_V1_STR}/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )
