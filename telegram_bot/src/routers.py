from aiogram import types
from aiogram.filters import CommandStart

from src.main import dp
from src.services.notification_service import NotificationService


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Reply with your email to register for notifications")


@dp.message()
async def capture_email(message: types.Message):
    tg_user_id = message.from_user.id
    email = message.text
    if await NotificationService.subscribe_user(tg_user_id, email):
        await message.answer("You've subscribed to message notifications")
    else:
        await message.answer('Use /start to register for notifications')