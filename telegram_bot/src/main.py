import asyncio
import logging
from aiohttp import web

from src.routers import dp
from src.settings import bot, server_settings
from src.utils import setup_logging
from src.api import notification_handler

setup_logging(logging.INFO)
logger = logging.getLogger(__name__)

web_app = web.Application()
web_app.router.add_post('/notification', notification_handler)


async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    logging.info('Bot started')


async def start_server():
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=server_settings.WEB_APP_PORT
    )
    await site.start()
    logger.info('Aiohttp server started')


async def main():
    bot_task = asyncio.create_task(start_bot())
    server_task = asyncio.create_task(start_server())
    await bot_task
    await server_task


if __name__ == '__main__':
    asyncio.run(main())
