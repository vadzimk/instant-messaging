import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from src.main import app
from src.db import Session
from src import models as m

test_user = {"first_name": "testname", "last_name": "", "email": "test@mail.com", "password": "secret"}

@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
async def signup_user_response():
    user_to_create = test_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/api/signup', json=user_to_create)
        yield res
        async with Session() as session:
            async with session.begin():
                test_user_from_db = await session.scalar(select(m.User).where(m.User.email == user_to_create['email']))
                if test_user_from_db:
                    await session.delete(test_user_from_db)


@pytest.fixture(scope='module')
async def login_user_response(signup_user_response):
    user_to_login = {
        'username': test_user.get('email'),
        'password': test_user.get('password')
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/api/login', data=user_to_login)  # send as form data
        yield res
