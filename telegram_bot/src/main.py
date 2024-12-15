import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src.routers import tg_router
from src.settings import server_settings
from src.api import notification_handler, webhook_handler

from src.logger import logger


class TelegramBotServer:
    WEBHOOK_PATH = f'/webhook'
    WEB_APP_HOST = '0.0.0.0'

    def __init__(self):
        self.web_app = web.Application()
        self.bot = Bot(token=server_settings.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()

        self._configure_app()

    def _configure_app(self):
        """ Configure web app and bot dispatcher """
        self.web_app.router.add_post('/notification', notification_handler)
        self.dp['dp'] = self.dp
        self.dp.include_router(tg_router)
        self.web_app['bot'] = self.bot
        self.web_app['dp'] = self.dp

    async def start_polling(self):
        """ start polling telegram server for messages for development environment """
        self.web_app.router.add_post(self.WEBHOOK_PATH, webhook_handler)
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    async def register_webhook(self):
        """ register webhook for production environment """
        SimpleRequestHandler(dispatcher=dp, bot=self.bot).register(self.web_app, path=self.WEBHOOK_PATH)
        setup_application(self.web_app, self.dp, bot=self.bot)
        webhook_url = f'{server_settings.WEBHOOK_URL_BASE}{self.WEBHOOK_PATH}'
        await self.bot.set_webhook(webhook_url)
        logging.info(f'Webhook set to {webhook_url}')

    async def stop_bot(self):
        """ stop bot session """
        await self.bot.session.close()

    async def stop_dispatcher(self):
        """ stop dispatcher storage """
        await self.dp.storage.close()

    async def start_server(self):
        """ start aiohttp server """
        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, self.WEB_APP_HOST, server_settings.WEB_APP_PORT)
        await site.start()

    async def start(self):
        """ main entrypoint to start server """
        try:
            if server_settings.ENV != 'production':
                await self.start_polling()
            else:  # production
                await self.register_webhook()

            await self.start_server()
        finally:  # cleanup on exit
            await self.stop_dispatcher()
            await self.stop_bot()
            await self.web_app.shutdown()


server = TelegramBotServer()

if __name__ == '__main__':
    asyncio.run(server.start())
