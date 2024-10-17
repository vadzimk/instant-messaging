import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from starlette import status
from starlette.testclient import TestClient
from src.app import app
from src.db import Session
from src import models as m



@pytest.fixture
async def registered_user_response():
    user_to_create = {"email": "test@mail.com", "password": "secret"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/register', json=user_to_create)
        yield res
        async with Session() as session:
            async with session.begin():
                test_user = await session.scalar(select(m.User).where(m.User.email == user_to_create['email']))
                if test_user:
                    await session.delete(test_user)


def test_register_user(registered_user_response):
    assert registered_user_response.status_code == status.HTTP_201_CREATED
    assert registered_user_response.json().get("msg") == "User registered successfully"
