from celery import Celery

from src.settings import server_settings

celery = Celery(
    __name__,
    broker=f'redis://{server_settings.REDIS_HOST}:{server_settings.REDIS_PORT}/{server_settings.REDIS_DB}',
    backend=f'redis://{server_settings.REDIS_HOST}:{server_settings.REDIS_PORT}/{server_settings.REDIS_DB}',
    # include=['src.celery_app.tasks'],
    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-imports
    imports=['src.celery_app.tasks'],
)
