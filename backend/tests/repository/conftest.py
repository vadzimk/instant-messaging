import asyncio
from typing import AsyncGenerator, List
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.user_repository import UserRepository
from src.db import Session

from tests.data.data import user1
from src import models as m


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()


async def insert_user_helper(user_fields, session) -> m.User:
    user_repository = UserRepository(session=session)
    user = m.User(**user_fields)
    return await user_repository.add(user)


@pytest.fixture
async def insert_user1(async_session) -> m.User:
    user_fields = {k: v for k, v in user1.model_dump().items() if k != 'password'}
    user_fields['hashed_password'] = user1.password
    user = await insert_user_helper(user_fields, async_session)
    yield user
    await async_session.delete(user)
    await async_session.commit()


@pytest.fixture
async def insert_users(request, async_session) -> AsyncGenerator[List[m.User], None]:
    users = []
    user_count = request.param
    for i in range(user_count):
        user_fields = {
            "email": f"u{i + 1}@mail.com",
            "first_name": f"u-test-repository-{i + 1}",
            "last_name": "u-test-repository-odd",
            "hashed_password": "secret"
        }
        if i % 2:
            user_fields['last_name'] = 'u-test-repository-even'
        user = await insert_user_helper(user_fields, async_session)
        users.append(user)
    yield users
    for user in users:
        await async_session.delete(user)
    await async_session.commit()
