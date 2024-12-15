import asyncio
import logging
import secrets

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src.routers import tg_router
from src.settings import server_settings
from src.api import notification_handler, webhook_handler

from src.logger import logger

# WEBHOOK_HEX = secrets.token_hex(32)
# WEBHOOK_PATH = f'/webhook/{WEBHOOK_HEX}'
WEBHOOK_PATH = f'/webhook'

web_app = web.Application()
web_app.router.add_post('/notification', notification_handler)
web_app.router.add_post(WEBHOOK_PATH, webhook_handler)

bot = Bot(token=server_settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

dp['dp'] = dp

dp.include_router(tg_router)
web_app['bot'] = bot

web_app['dp'] = dp

is_polling = False


async def start_bot():
    """ set webhook on telegram server in production """
    global is_polling
    if server_settings.ENV != 'production':
        await bot.delete_webhook(drop_pending_updates=True)
        try:
            await dp.start_polling(bot)
            is_polling = True
        finally:
            is_polling = False
    else:
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(web_app, path=WEBHOOK_PATH)
        setup_application(web_app, dp, bot=bot)
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


async def stop_bot():
    """ close bots aiohttp session """
    await bot.session.close()


async def stop_dispatcher():
    if is_polling:
        await dp.stop_polling()
    await dp.storage.close()


async def main():
    try:
        await asyncio.create_task(start_bot())
        await asyncio.create_task(start_server())
    finally:  # cleanup on exit
        await stop_dispatcher()
        await stop_bot()


if __name__ == '__main__':
    asyncio.run(main())
