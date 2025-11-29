"""
Celery application configuration for background tasks.
"""

from celery import Celery

from app.config import settings


# Instantiate the Celery application.
celery = Celery(
    "afroken",  # Name used for the Celery app and in the worker logs.
    broker=settings.REDIS_URL,  # Redis URL acts as the message broker.
    backend=settings.REDIS_URL,  # Redis also used to store task results.
)

# Route tasks whose fully qualified name starts with `app.tasks.document_tasks.`
# to a dedicated "documents" queue so they can be handled by specific workers.
celery.conf.task_routes = {
    "app.tasks.document_tasks.*": {"queue": "documents"},
}

