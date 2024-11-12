from aiogram import types, Dispatcher
from aiogram.filters import CommandStart

from src.services.notification_service import NotificationService

dp = Dispatcher()  # must register messages before start polling


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Reply with your email to register for notifications")


@dp.message()
async def capture_email(message: types.Message):
    tg_user_id = message.from_user.id
    email = message.text
    await message.answer(
        await NotificationService.subscribe_user(tg_user_id, email)
    )
