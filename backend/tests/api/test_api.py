import asyncio
from pathlib import Path

import jwt
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from starlette import status
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


def test_signup_user(signup_user_response):
    assert signup_user_response.status_code == status.HTTP_201_CREATED
    assert signup_user_response.json().get("email") == test_user.get('email')
    print(signup_user_response.json())


@pytest.fixture(scope='session')
async def login_user_response(signup_user_response):
    user_to_login = test_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        res = await client.post('/api/login', json=user_to_login)
        yield res


def decode_access_token(access_token):
    # validate token on the client for each request
    private_key_path = Path(__file__).parent.parent.parent / 'jwt_keys/public_key.pem'
    public_key_text = private_key_path.read_text()
    public_key = load_pem_x509_certificate(public_key_text.encode('utf-8')).public_key()
    validated_result_payload = jwt.decode(access_token, key=public_key, algorithms=['RS256'],
                                          audience=["http://127.0.0.1:8000/"])
    return validated_result_payload


@pytest.mark.xfail(reason="using cookie for authentication")
async def test_login_user_using_authorization_header(login_user_response):
    data = login_user_response.json()
    print(data)
    assert data.get('token_type') == 'bearer', "json body bearer not set"
    access_token = data.get('access_token')
    validated_result_payload = decode_access_token(access_token)
    print("validated_result_payload")
    print(validated_result_payload)
    assert validated_result_payload.get('sub') == test_user.get('email'), "token subject not set to email"



async def test_login_user_using_cookie(login_user_response):
    access_token = login_user_response.cookies.get('access_token')
    assert access_token is not None, "Access token cookie not set"
    print(access_token)
    validated_result_payload = decode_access_token(access_token)
    assert validated_result_payload.get('sub') == test_user.get('email'), "token subject not set to email"


@pytest.fixture(scope="session")
async def authenticate_user_with_header_response(login_user_response):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        auth_header = f'Bearer {login_user_response.json().get("access_token")}'
        res = await client.post('/api/me', headers={'Authorization': auth_header})
        yield res


async def test_authenticated_request_rejects_if_not_authenticated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        auth_header = f'Bearer xxx.xxx.xxx'
        res = await client.post('/api/me', headers={'Authorization': auth_header})
    print(res.status_code)
    print(res.json())
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, "unauthenticated request is not rejected on protected path"


@pytest.mark.xfail(reason="using cookie authentication")
async def test_authenticated_request_accepts_valid_header(authenticate_user_with_header_response):
    print(authenticate_user_with_header_response.status_code)
    print(authenticate_user_with_header_response.json())
    assert authenticate_user_with_header_response.status_code == status.HTTP_200_OK, "authenticated request is rejected on protected path"


@pytest.fixture(scope="session")
async def authenticate_user_with_cookie_response(login_user_response):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        access_token = login_user_response.cookies.get('access_token')
        print('---access_token', access_token)
        client.cookies.set('access_token', access_token, domain='test', path='/')
        res = await client.post('/api/me')
        yield res

@pytest.mark.only
async def test_authenticated_request_accepts_valid_cookie(authenticate_user_with_cookie_response):
    print(authenticate_user_with_cookie_response.json())
    assert authenticate_user_with_cookie_response.status_code == status.HTTP_200_OK, "authenticaed request is rejected on protected path"
