from fastapi import APIRouter, HTTPException
from typing import Dict
import logging
from ..core.redis_client import redis_manager
from ..services.tiny_client import tiny_client

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check básico"""
    try:
        # Verifica Redis
        redis_ok = await redis_manager.health_check()
        
        status = "healthy" if redis_ok else "degraded"
        
        return {
            "status": status,
            "redis": "ok" if redis_ok else "error",
            "version": "2.0"
        }
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Health check detalhado com todas as dependências"""
    results = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check Redis
    try:
        redis_ok = await redis_manager.health_check()
        results["checks"]["redis"] = {
            "status": "ok" if redis_ok else "error",
            "responsive": redis_ok
        }
    except Exception as e:
        results["checks"]["redis"] = {
            "status": "error",
            "error": str(e)
        }
        results["status"] = "unhealthy"
    
    # Check Tiny API (apenas verifica se token está configurado)
    results["checks"]["tiny_api"] = {
        "status": "ok" if tiny_client.token else "error",
        "configured": bool(tiny_client.token)
    }
    
    if not tiny_client.token:
        results["status"] = "degraded"
    
    return results