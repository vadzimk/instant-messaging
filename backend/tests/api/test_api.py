import asyncio
import os
from pathlib import Path

import jwt
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from starlette import status
from starlette.testclient import TestClient
from src.main import app
from src.db import Session
from src import models as m
from cryptography.x509 import load_pem_x509_certificate

test_user = {"email": "test@mail.com", "password": "secret"}


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
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
                test_user_from_db = await session.scalar(select(m.User).where(m.User.email == user_to_create['email']))
                if test_user_from_db:
                    await session.delete(test_user_from_db)


@pytest.mark.parametrize('registered_user_response, expected_email',
                         [(test_user, test_user.get('email'))], indirect=['registered_user_response'])
def test_register_user(registered_user_response, expected_email):
    assert registered_user_response.status_code == status.HTTP_201_CREATED
    assert registered_user_response.json().get("email") == expected_email
    print(registered_user_response.json())


@pytest.mark.parametrize('registered_user_response', [test_user], indirect=['registered_user_response'])
async def test_login_user(registered_user_response):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/login', json=test_user)
    data = res.json()
    print(data)
    assert data.get('token_type') == 'bearer'
    # validate token on the client for each request
    private_key_path = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / 'jwt_keys/public_key.pem'
    public_key_text = private_key_path.read_text()
    public_key = load_pem_x509_certificate(public_key_text.encode('utf-8')).public_key()
    access_token = data.get('access_token')
    validated_result_payload = jwt.decode(access_token, key=public_key, algorithms=['RS256'],
                                          audience=["http://127.0.0.1:8000/"])
    print("validated_result_payload")
    print(validated_result_payload)
    assert validated_result_payload.get('sub') == test_user.get('email')

