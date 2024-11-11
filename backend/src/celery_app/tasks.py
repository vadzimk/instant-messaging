import asyncio

import aiohttp
from celery.utils.log import get_task_logger

from src.celery_app.worker import celery
from src.settings import server_settings

celery_logger = get_task_logger(__name__)


@celery.task
def send_telegram_notification(tg_user_id: int, content: str):
    """ wrapper around async task for Celery compatibility """
    asyncio.run(_send_telegram_notification(tg_user_id, content))


async def _send_telegram_notification(tg_user_id: int, content: str):
    payload = {'tg_user_id': tg_user_id, 'content': content}
    async with aiohttp.ClientSession() as session:
        async with session.post(server_settings.BOT_BASE_URL + '/notification', json=payload) as response:
            response_data = await response.json()
            if response.status != 204:
                celery_logger.error(f'Notification failed for tg_user_id: {tg_user_id}. Reason: {response_data}')
