import redis
from .config import config
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client = None
        self.connected = False
        try:
            self.client = redis.from_url(
                config.REDIS_URL, 
                decode_responses=True
            )
            self.client.ping()
            self.connected = True
            logger.info("Conexão Redis estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar com Redis: {e}")
            logger.warning("Aplicativo iniciará sem Redis. Algumas funcionalidades estarão limitadas.")
            self.connected = False
    
    def get(self, key: str) -> Optional[Any]:
        """Busca valor no Redis"""
        if not self.connected or not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar {key} no Redis: {e}")
            return None
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Salva valor no Redis"""
        if not self.connected or not self.client:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Erro ao salvar {key} no Redis: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove chave do Redis"""
        if not self.connected or not self.client:
            return False
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Erro ao deletar {key} no Redis: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self.connected or not self.client:
            return False
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar {key} no Redis: {e}")
            return False

class DummyRedisClient:
    """Cliente Redis falso para quando Redis não está disponível"""
    def get(self, key: str) -> None:
        return None
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        return False
    
    def delete(self, key: str) -> bool:
        return False
    
    def exists(self, key: str) -> bool:
        return False

# Instância global
try:
    redis_client = RedisClient()
except Exception as e:
    logger.error(f"Falha ao criar cliente Redis: {e}")
    logger.warning("Usando cliente Redis falso")
    redis_client = DummyRedisClient()