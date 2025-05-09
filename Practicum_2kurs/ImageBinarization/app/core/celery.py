from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=str(settings.REDIS_URL),  # Конвертируем RedisDsn в строку
    backend=str(settings.REDIS_URL))

celery_app.conf.task_routes = {
    "app.worker.test_celery": "main-queue",
}