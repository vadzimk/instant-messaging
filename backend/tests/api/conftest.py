from typing import Generator, AsyncGenerator
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport, Response
from sqlalchemy import select
from src.main import app
from src.db import Session
from src import models as m
from src.api import schemas as p


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
def user1() -> Generator[p.CreateUserSchema, None, None]:
    test_user = p.CreateUserSchema(
        email="u1@mail.com",
        first_name="u1",
        last_name="",
        password="secret"
    )
    yield test_user


@pytest.fixture(scope='function')
def user2() -> Generator[p.CreateUserSchema, None, None]:
    test_user = p.CreateUserSchema(
        email="u2@mail.com",
        first_name="u2",
        last_name="",
        password="secret"
    )
    yield test_user


async def signup_user_helper(user_to_create: p.CreateUserSchema) -> AsyncGenerator[Response, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/api/users', json=user_to_create.model_dump())
    yield res
    # delete created user
    async with Session() as session:
        async with session.begin():
            test_user_from_db = await session.scalar(select(m.User).where(m.User.email == res.json().get('email')))
            if test_user_from_db:
                await session.delete(test_user_from_db)


@pytest.fixture(scope='function')
async def signup_user1_response(user1) -> AsyncGenerator[Response, None]:
    signup_res_iterator = signup_user_helper(user1)
    signup_res = await anext(signup_res_iterator)
    yield signup_res
    try:
        await anext(signup_res_iterator)  # cleanup
    except StopAsyncIteration:
        pass  # expected


@pytest.fixture(scope='function')
async def signup_user2_response(user2) -> AsyncGenerator[Response, None]:
    signup_res_iterator = signup_user_helper(user2)
    signup_res = await anext(signup_res_iterator)
    yield signup_res
    try:
        await anext(signup_res_iterator)  # cleanup
    except StopAsyncIteration:
        pass  # expected


@pytest.fixture(scope='function')
async def login_user1_response(signup_user1_response, user1) -> AsyncGenerator[Response, None]:
    user_to_login = {
        'username': user1.email,
        'password': user1.password
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/api/users/login', data=user_to_login)  # send as form data
        yield res
