import asyncio
import datetime
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from aiogram import types, Bot, types

from src.main import dp
from src.routers import start, capture_email


# @pytest.fixture
# async def bot_instance() -> Bot:
#     from src.main import bot
#     async with bot:
#         dp.loop = asyncio.get_event_loop()
#         yield bot


#  https://github.com/aiogram/aiogram/issues/378#issuecomment-663208333
async def test_start():
    expected_answer = "Reply with your email to register for notifications"
    message_mock = AsyncMock(text='/start')
    await start(message=message_mock)
    message_mock.answer.assert_called_with(expected_answer)


async def test_capture_email():  # TODO implement backend endpoint to subscribe user
    message_mock = AsyncMock(from_user=AsyncMock(id=123), text='hello@mail.com')
    await capture_email(message_mock)
    message_mock.answer.assert_called_with('Use /start to register for notifications')