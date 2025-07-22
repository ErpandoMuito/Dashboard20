"""
Health check endpoints.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from app.models.base import BaseResponse
from app.services.redis_service import redis_service
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=BaseResponse)
async def health_check():
    """Basic health check endpoint."""
    return BaseResponse(
        success=True,
        message="API is healthy",
        data={
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )


@router.get("/health/detailed", response_model=BaseResponse)
async def detailed_health_check():
    """Detailed health check with service status."""
    services_status = {}
    
    # Check Redis
    try:
        await redis_service._client.ping()
        services_status["redis"] = {
            "status": "healthy",
            "message": "Redis is responding"
        }
    except Exception as e:
        services_status["redis"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # Overall status
    all_healthy = all(
        service["status"] == "healthy" 
        for service in services_status.values()
    )
    
    return BaseResponse(
        success=all_healthy,
        message="System health check",
        data={
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "services": services_status
        }
    )