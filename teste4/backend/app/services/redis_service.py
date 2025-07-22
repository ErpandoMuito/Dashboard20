"""
Redis service for caching and pub/sub.
"""
import json
from typing import Optional, Any, List, Dict
from datetime import timedelta
import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisService:
    """Service for Redis operations."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self._client = await redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
                health_check_interval=30
            )
            await self._client.ping()
            logger.info("Connected to Redis", url=settings.REDIS_URL)
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._pubsub:
            await self._pubsub.close()
        if self._client:
            await self._client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Redis GET error", key=key, error=str(e))
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None,
        expire_timedelta: Optional[timedelta] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        try:
            serialized = json.dumps(value, default=str)
            
            if expire_timedelta:
                expire = int(expire_timedelta.total_seconds())
            
            if expire:
                await self._client.setex(key, expire, serialized)
            else:
                await self._client.set(key, serialized)
            
            return True
        except Exception as e:
            logger.error("Redis SET error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            result = await self._client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error("Redis DELETE error", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.error("Redis EXISTS error", key=key, error=str(e))
            return False
    
    async def scan_keys(self, pattern: str, count: int = 100) -> List[str]:
        """Scan for keys matching pattern."""
        keys = []
        try:
            cursor = 0
            while True:
                cursor, batch = await self._client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=count
                )
                keys.extend(batch)
                if cursor == 0:
                    break
            return keys
        except Exception as e:
            logger.error("Redis SCAN error", pattern=pattern, error=str(e))
            return []
    
    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values at once."""
        try:
            values = await self._client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error("Redis MGET error", error=str(e))
            return {}
    
    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel."""
        try:
            serialized = json.dumps(message, default=str)
            return await self._client.publish(channel, serialized)
        except Exception as e:
            logger.error("Redis PUBLISH error", channel=channel, error=str(e))
            return 0
    
    async def subscribe(self, channels: List[str]):
        """Subscribe to channels."""
        try:
            self._pubsub = self._client.pubsub()
            await self._pubsub.subscribe(*channels)
            logger.info("Subscribed to channels", channels=channels)
        except Exception as e:
            logger.error("Redis SUBSCRIBE error", channels=channels, error=str(e))
            raise
    
    async def get_message(self, timeout: Optional[float] = None) -> Optional[Dict]:
        """Get message from subscribed channels."""
        if not self._pubsub:
            return None
        
        try:
            message = await self._pubsub.get_message(timeout=timeout)
            if message and message["type"] == "message":
                message["data"] = json.loads(message["data"])
            return message
        except Exception as e:
            logger.error("Redis GET_MESSAGE error", error=str(e))
            return None
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        try:
            return await self._client.incrby(key, amount)
        except Exception as e:
            logger.error("Redis INCR error", key=key, error=str(e))
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        try:
            return await self._client.expire(key, seconds)
        except Exception as e:
            logger.error("Redis EXPIRE error", key=key, error=str(e))
            return False
    
    async def ttl(self, key: str) -> int:
        """Get time to live for a key."""
        try:
            return await self._client.ttl(key)
        except Exception as e:
            logger.error("Redis TTL error", key=key, error=str(e))
            return -2
    
    async def sadd(self, key: str, *members: str) -> int:
        """Add members to a set."""
        try:
            return await self._client.sadd(key, *members)
        except Exception as e:
            logger.error("Redis SADD error", key=key, error=str(e))
            return 0
    
    async def smembers(self, key: str) -> set:
        """Get all members of a set."""
        try:
            return await self._client.smembers(key)
        except Exception as e:
            logger.error("Redis SMEMBERS error", key=key, error=str(e))
            return set()
    
    async def srem(self, key: str, *members: str) -> int:
        """Remove members from a set."""
        try:
            return await self._client.srem(key, *members)
        except Exception as e:
            logger.error("Redis SREM error", key=key, error=str(e))
            return 0


# Singleton instance
redis_service = RedisService()