"""
Health check endpoint.
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import aiohttp

from app.core.database import get_db
from app.cache import CacheClient
from app.core.config import settings


router = APIRouter()


async def check_database(db: AsyncSession) -> bool:
    """Check PostgreSQL database connection."""
    try:
        result = await db.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_redis(cache: CacheClient) -> bool:
    """Check Redis connection."""
    try:
        await cache.set("health_check", "ok", ttl=10)
        value = await cache.get("health_check")
        return value == "ok"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False


async def check_elasticsearch() -> bool:
    """Check Elasticsearch connection."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.ELASTICSEARCH_URL}/_cluster/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('status') in ['yellow', 'green']
                return False
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        return False


async def check_tika() -> bool:
    """Check Apache Tika server."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.TIKA_SERVER_URL}/tika",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"Tika health check failed: {e}")
        return False


@router.get("")
async def health_check(
    db: AsyncSession = Depends(get_db),
    cache: CacheClient = Depends(lambda: CacheClient())
):
    """
    Comprehensive health check endpoint.
    
    Returns:
        Health status of all system components
    """
    try:
        # Check all services in parallel
        db_status, redis_status, es_status, tika_status = await asyncio.gather(
            check_database(db),
            check_redis(cache),
            check_elasticsearch(),
            check_tika(),
            return_exceptions=True
        )
        
        # Handle exceptions
        db_ok = db_status if isinstance(db_status, bool) else False
        redis_ok = redis_status if isinstance(redis_status, bool) else False
        es_ok = es_status if isinstance(es_status, bool) else False
        tika_ok = tika_status if isinstance(tika_status, bool) else False
        
        # Determine overall health
        all_healthy = all([db_ok, redis_ok, es_ok, tika_ok])
        
        response = {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "api": {"status": "up", "healthy": True},
                "database": {"status": "up" if db_ok else "down", "healthy": db_ok},
                "redis": {"status": "up" if redis_ok else "down", "healthy": redis_ok},
                "elasticsearch": {"status": "up" if es_ok else "down", "healthy": es_ok},
                "tika": {"status": "up" if tika_ok else "down", "healthy": tika_ok}
            },
            "environment": settings.ENVIRONMENT
        }
        
        # Return 503 if critical services are down
        if not (db_ok and redis_ok):
            logger.warning("Critical services are down")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=response
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db)
):
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 if the service is ready to accept traffic.
    """
    try:
        # Quick database check
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return {"status": "ready"}
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    
    Returns 200 if the service is alive (but may not be ready).
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
