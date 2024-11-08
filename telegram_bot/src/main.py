import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.settings import configure_server_settings
from src.utils import setup_logging

server_settings = configure_server_settings()

dp = Dispatcher()
bot = Bot(token=server_settings.TELEGRAM_BOT_TOKEN)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # for webhook method need public ip
    logging.info('Bot started')


if __name__ == '__main__':
    setup_logging(logging.INFO)
    asyncio.run(main())
