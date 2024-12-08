import asyncio
import logging
import secrets

from aiohttp import web

from src.routers import dp
from src.settings import bot, server_settings
from src.utils import setup_logging
from src.api import notification_handler, webhook_handler

setup_logging(logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_HEX = secrets.token_hex(32)
WEBHOOK_PATH = f'/webhook/{WEBHOOK_HEX}'

web_app = web.Application()
web_app.router.add_post('/notification', notification_handler)
web_app.router.add_post(WEBHOOK_PATH, webhook_handler)


async def start_bot():
    """ set webhook on telegram server in production """
    if server_settings.ENV == 'development':
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    else:
        webhook_url = f'{server_settings.WEBHOOK_URL_BASE}/{WEBHOOK_PATH}'
        await bot.set_webhook(webhook_url)
        logging.info(f'Webhook set to {webhook_url}')
    logging.info(f'Bot started')


async def start_server():
    """ start aiohttp web server """
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=server_settings.WEB_APP_PORT
    )
    await site.start()
    logger.info(f'Aiohttp server started on port {server_settings.WEB_APP_PORT}')


async def main():
    bot_task = asyncio.create_task(start_bot())
    server_task = asyncio.create_task(start_server())
    await bot_task
    await server_task


if __name__ == '__main__':
    asyncio.run(main())
