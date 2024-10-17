import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from starlette import status
from starlette.testclient import TestClient
from src.app import app
from src.db import Session
from src import models as m


@pytest.fixture
async def registered_user_response(request):
    """
    :param request: {"email": "test@mail.com", "password": "secret"}
    """
    user_to_create = request.param
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/register', json=user_to_create)
        yield res
        async with Session() as session:
            async with session.begin():
                test_user = await session.scalar(select(m.User).where(m.User.email == user_to_create['email']))
                if test_user:
                    await session.delete(test_user)


@pytest.mark.parametrize('registered_user_response, expected_email',
                         [({"email": "test@mail.com", "password": "secret"}, "test@mail.com")], indirect=['registered_user_response'])
def test_register_user(registered_user_response, expected_email):
    assert registered_user_response.status_code == status.HTTP_201_CREATED
    assert registered_user_response.json().get("email") == expected_email
    print(registered_user_response.json())
