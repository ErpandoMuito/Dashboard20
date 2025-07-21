import redis
from .config import settings
import json
from typing import Optional, Any

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor no Redis"""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Salva valor no Redis"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> bool:
        """Remove chave do Redis"""
        return self.client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        return self.client.exists(key) > 0

# Instância global
redis_client = RedisClient()