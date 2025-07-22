"""
Celery tasks for background processing.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import Task
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.services.redis_service import redis_service
from app.services.tiny_api import TinyAPIClient
from app.core.config import settings

logger = get_task_logger(__name__)


class CallbackTask(Task):
    """Base task with callbacks."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Success callback."""
        logger.info(f"Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback."""
        logger.error(f"Task {task_id} failed with exception: {exc}")


@celery_app.task(bind=True, base=CallbackTask, name="app.workers.tasks.sync_notas_fiscais")
def sync_notas_fiscais(self) -> Dict[str, Any]:
    """
    Sincroniza notas fiscais com Tiny ERP.
    """
    try:
        logger.info("Starting notas fiscais sync")
        
        # Initialize Tiny API client
        tiny_client = TinyAPIClient(token=settings.TINY_API_TOKEN)
        
        # Get last sync timestamp
        last_sync = redis_service.get("sync:notas:last_timestamp")
        if last_sync:
            data_inicial = datetime.fromisoformat(last_sync)
        else:
            # Default to 30 days ago
            data_inicial = datetime.now() - timedelta(days=30)
        
        # Sync notas
        result = tiny_client.sync_notas_fiscais(
            data_inicial=data_inicial.strftime("%d/%m/%Y"),
            data_final=datetime.now().strftime("%d/%m/%Y")
        )
        
        # Update last sync timestamp
        redis_service.set(
            "sync:notas:last_timestamp",
            datetime.now().isoformat(),
            ex=86400  # Expire in 24 hours
        )
        
        logger.info(f"Sync completed: {result}")
        return {
            "success": True,
            "synced_count": result.get("count", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error syncing notas fiscais: {e}")
        raise


@celery_app.task(bind=True, base=CallbackTask, name="app.workers.tasks.process_pedido_upload")
def process_pedido_upload(self, file_path: str, cliente: str) -> Dict[str, Any]:
    """
    Processa upload de pedido em background.
    """
    try:
        logger.info(f"Processing pedido upload: {file_path} for client {cliente}")
        
        # TODO: Implement PDF parsing logic
        # For now, just simulate processing
        import time
        time.sleep(2)  # Simulate processing time
        
        result = {
            "success": True,
            "file": file_path,
            "cliente": cliente,
            "processed_items": 10,  # Mock data
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Upload processed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing pedido upload: {e}")
        raise


@celery_app.task(bind=True, base=CallbackTask, name="app.workers.tasks.cleanup_old_data")
def cleanup_old_data(self) -> Dict[str, Any]:
    """
    Limpa dados antigos do cache Redis.
    """
    try:
        logger.info("Starting old data cleanup")
        
        # Get all keys with pattern
        deleted_count = 0
        patterns = ["nota:*", "pedido:*", "temp:*"]
        
        for pattern in patterns:
            keys = redis_service.scan_keys(pattern)
            for key in keys:
                # Check if key is expired or old
                ttl = redis_service.ttl(key)
                if ttl == -1:  # No expiration set
                    # Set expiration to 30 days
                    redis_service.expire(key, 2592000)
                    deleted_count += 1
        
        logger.info(f"Cleanup completed: {deleted_count} keys updated")
        return {
            "success": True,
            "cleaned_count": deleted_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise


@celery_app.task(bind=True, base=CallbackTask, name="app.workers.tasks.generate_report")
def generate_report(self, report_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera relatórios em background.
    """
    try:
        logger.info(f"Generating report: {report_type} with params: {params}")
        
        # TODO: Implement report generation logic
        # For now, just simulate
        import time
        time.sleep(5)  # Simulate report generation
        
        report_id = f"report_{report_type}_{datetime.now().timestamp()}"
        
        # Store report metadata in Redis
        redis_service.set(
            f"report:{report_id}",
            {
                "type": report_type,
                "params": params,
                "status": "completed",
                "generated_at": datetime.now().isoformat()
            },
            ex=3600  # Expire in 1 hour
        )
        
        logger.info(f"Report generated: {report_id}")
        return {
            "success": True,
            "report_id": report_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise