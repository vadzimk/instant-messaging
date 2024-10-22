import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from src.main import app
from src.db import Session
from src import models as m

from src.api.schemas import UserCreateIn


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
def user() -> UserCreateIn:
    test_user = UserCreateIn(
        email="test@mail.com",
        first_name="testname",
        last_name="",
        password="secret"
    )
    yield test_user


async def signup_user_helper(user_to_create: UserCreateIn):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/api/signup', json=user_to_create.model_dump())
    yield res
    # delete created user
    async with Session() as session:
        async with session.begin():
            test_user_from_db = await session.scalar(select(m.User).where(m.User.email == res.json().get('email')))
            if test_user_from_db:
                await session.delete(test_user_from_db)


@pytest.fixture(scope='function')
async def signup_user_response(user):
    signup_res_iterator = signup_user_helper(user)
    signup_res = await anext(signup_res_iterator)
    yield signup_res
    try:
        await anext(signup_res_iterator)  # cleanup
    except StopAsyncIteration:
        pass  # expected


@pytest.fixture(scope='function')
async def login_user_response(signup_user_response, user):
    user_to_login = {
        'username': user.email,
        'password': user.password
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/api/login', data=user_to_login)  # send as form data
        yield res
