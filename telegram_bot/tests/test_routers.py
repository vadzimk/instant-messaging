from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from src.routers import start, capture_email


#  https://github.com/aiogram/aiogram/issues/378#issuecomment-663208333
async def test_start():
    expected_answer = "Reply with your email to register for notifications"
    message_mock = AsyncMock(text='/start')
    await start(message=message_mock)
    message_mock.answer.assert_called_with(expected_answer)


async def test_capture_email_fails_when_user_email_exists_not():
    non_existing_user_email = 'hello@mail.com'
    expected_answer = f"Failed to subscribe\nUser with email: {non_existing_user_email} does not exist\nUse /start to try again to register for notifications"
    message_mock = AsyncMock(from_user=AsyncMock(id=123), text=non_existing_user_email)
    await capture_email(message_mock)
    message_mock.answer.assert_called_with(expected_answer)


@pytest.mark.asyncio(loop_scope='session')
async def test_capture_email_succeeds_when_user_email_exists(create_user1, db_session, load_tables):
    existing_user_email = create_user1.get('email')
    expected_answer = "You've subscribed to message notifications"
    message_mock = AsyncMock(from_user=AsyncMock(id=123), text=existing_user_email)
    await capture_email(message_mock)
    message_mock.answer.assert_called_with(expected_answer)

    # check user updated in database
    q = select(load_tables.User).where(load_tables.User.c.email == existing_user_email)
    res = await db_session.execute(q)
    user_from_db = res.fetchone()
    user_from_db_dict = None
    if user_from_db:
        user_from_db_dict = dict(zip(res.keys(), user_from_db))

    print('updated_user', user_from_db_dict)
    assert user_from_db_dict.get(
        'telegram_id') == message_mock.from_user.id, f"telegram_id column in db does not have expected value"
