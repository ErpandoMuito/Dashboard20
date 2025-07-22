import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from typing import Optional, Any, List, Dict
import logging
import json
from .config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Gerenciador Redis com reconnect automático e retry"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._retry = Retry(
            ExponentialBackoff(),
            retries=3,
            supported_errors=(
                ConnectionError,
                TimeoutError,
                redis.ConnectionError,
                redis.TimeoutError,
            )
        )
    
    async def connect(self):
        """Conecta ao Redis com configurações robustas"""
        try:
            self.client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=settings.redis_decode_responses,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                retry_on_timeout=settings.redis_retry_on_timeout,
                retry=self._retry,
                health_check_interval=settings.redis_health_check_interval,
                max_connections=settings.redis_max_connections,
            )
            # Test connection
            await self.client.ping()
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")
            raise
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.client:
            await self.client.close()
            logger.info("Desconectado do Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get com tratamento de erro e fallback"""
        try:
            value = await self.client.get(key)
            if value and value.startswith('{'):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        except Exception as e:
            logger.error(f"Erro ao buscar {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set com serialização automática"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            await self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete com tratamento de erro"""
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Erro ao deletar {keys}: {e}")
            return 0
    
    async def scan_keys(self, pattern: str, count: int = 100) -> List[str]:
        """Scan seguro sem usar keys()"""
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern, count=count):
                keys.append(key)
            return keys
        except Exception as e:
            logger.error(f"Erro ao escanear padrão {pattern}: {e}")
            return []
    
    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Multi-get com tratamento de erro"""
        try:
            values = await self.client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value) if value.startswith('{') else value
                    except json.JSONDecodeError:
                        result[key] = value
            return result
        except Exception as e:
            logger.error(f"Erro no mget: {e}")
            return {}
    
    async def pipeline_execute(self, commands: List[tuple]) -> List[Any]:
        """Executa comandos em pipeline"""
        try:
            async with self.client.pipeline() as pipe:
                for cmd, *args in commands:
                    getattr(pipe, cmd)(*args)
                return await pipe.execute()
        except Exception as e:
            logger.error(f"Erro no pipeline: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Verifica saúde da conexão"""
        try:
            await self.client.ping()
            return True
        except Exception:
            return False

# Singleton instance
redis_manager = RedisManager()