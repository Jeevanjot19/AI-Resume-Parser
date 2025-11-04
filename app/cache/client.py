"""
Redis cache client and utilities.
"""

import json
from typing import Optional, Any
import redis.asyncio as aioredis
from loguru import logger

from app.core.config import settings


class CacheClient:
    """Redis cache client wrapper."""
    
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = await aioredis.from_url(
                str(settings.get_redis_url()),
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.MAX_CONNECTIONS_COUNT
            )
            
            # Test connection
            await self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key} from cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key} from cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {key}: {e}")
            return 0
    
    async def set_with_lock(
        self,
        key: str,
        value: Any,
        lock_timeout: int = 10,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value with distributed lock."""
        lock_key = f"lock:{key}"
        try:
            # Acquire lock
            lock_acquired = await self.client.set(
                lock_key,
                "1",
                nx=True,
                ex=lock_timeout
            )
            
            if not lock_acquired:
                return False
            
            # Set value
            result = await self.set(key, value, ttl)
            
            # Release lock
            await self.client.delete(lock_key)
            
            return result
        except Exception as e:
            logger.error(f"Error in set_with_lock for key {key}: {e}")
            await self.client.delete(lock_key)
            return False


# Global cache client instance
cache_client = CacheClient()


async def get_cache_client() -> CacheClient:
    """Get cache client instance."""
    return cache_client


# Cache key builders
def build_resume_cache_key(resume_id: str) -> str:
    """Build cache key for resume."""
    return f"resume:{resume_id}"


def build_match_cache_key(resume_id: str, job_id: str) -> str:
    """Build cache key for resume-job match."""
    return f"match:{resume_id}:{job_id}"


def build_search_cache_key(query: str, filters: str) -> str:
    """Build cache key for search results."""
    return f"search:{query}:{filters}"
