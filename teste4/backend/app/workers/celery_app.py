"""
Celery application configuration and tasks.
"""
from celery import Celery
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "dashboard_next",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "sync-tiny-notas": {
        "task": "app.workers.tasks.sync_notas_fiscais",
        "schedule": 3600.0,  # Every hour
        "options": {"queue": "sync"}
    },
    "cleanup-old-data": {
        "task": "app.workers.tasks.cleanup_old_data",
        "schedule": 86400.0,  # Every day
        "options": {"queue": "maintenance"}
    },
}

# Task routes
celery_app.conf.task_routes = {
    "app.workers.tasks.sync_*": {"queue": "sync"},
    "app.workers.tasks.process_*": {"queue": "process"},
    "app.workers.tasks.cleanup_*": {"queue": "maintenance"},
}