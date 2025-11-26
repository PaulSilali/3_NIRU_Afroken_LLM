from celery import Celery

from app.config import settings


celery = Celery(
    "afroken",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.task_routes = {
    "app.tasks.document_tasks.*": {"queue": "documents"},
}



