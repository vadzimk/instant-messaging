import asyncio
import logging

from aiogram import Dispatcher
from aiohttp import web
from src.settings import bot, server_settings
from src.utils import setup_logging
from src.api import notification_handler

setup_logging(logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()

web_app = web.Application()
web_app.router.add_post('/notification', notification_handler)


async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # for webhook method need public ip
    logging.info('Bot started')


async def start_server():
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        host="0.0.0.0",  # accepts connections from all ip addresses
        port=server_settings.WEB_APP_PORT
    )
    await site.start()
    logger.info('Aiohttp server started')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    loop.create_task(start_server())
    loop.run_forever()
