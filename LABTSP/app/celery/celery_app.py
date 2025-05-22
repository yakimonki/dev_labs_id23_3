import os
from celery import Celery
from redislite import Redis

# Create Redis instance using redislite
redis_instance = Redis('redis.db')

# Configure Celery
celery_app = Celery(
    'tsp_tasks',
    broker=f'redis://{redis_instance.socket_file}',
    backend=f'redis://{redis_instance.socket_file}'
)

# Optional configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
) 