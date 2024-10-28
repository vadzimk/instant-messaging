from typing import Generator, AsyncGenerator, Tuple
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport, Response
from sqlalchemy import select
from pathlib import Path
from cryptography.x509 import load_pem_x509_certificate
import socketio
import jwt

from src.api.schemas import CreateContactSchema
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


def decode_access_token(access_token):
    # validate token on the client for each request
    private_key_path = Path(__file__).parent.parent.parent / 'jwt_keys/public_key.pem'
    public_key_text = private_key_path.read_text()
    public_key = load_pem_x509_certificate(public_key_text.encode('utf-8')).public_key()
    validated_result_payload = jwt.decode(access_token, key=public_key, algorithms=['RS256'],
                                          audience=["http://127.0.0.1:8000/"])
    return validated_result_payload


@pytest.fixture
async def client_with_auth_user1(login_user1_response) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        client.headers.update({
            'Authorization': f'Bearer {login_user1_response.json().get("access_token")}'
        })
        yield client


@pytest.fixture
async def create_u2_contact_for_u1_response(client_with_auth_user1, signup_user2_response):
    new_contact = CreateContactSchema(**signup_user2_response.json())
    return await client_with_auth_user1.post(
        '/api/contacts',
        json=new_contact.model_dump()
    )


@pytest.fixture
async def socketio_client_w_auth_u1(login_user1_response) -> AsyncGenerator[socketio.AsyncSimpleClient, None]:
    access_token = login_user1_response.json().get("access_token")
    client = socketio.AsyncSimpleClient()
    await client.connect('http://localhost:8000', auth={"token": access_token})
    yield client
    await client.disconnect()


@pytest.fixture
async def socketio_client_no_auth() -> AsyncGenerator[socketio.AsyncSimpleClient, None]:
    client = socketio.AsyncSimpleClient()
    try:
        await client.connect('http://localhost:8000', wait_timeout=2)
    except socketio.exceptions.ConnectionError:
        client = None
    yield client
    if client:
        await client.disconnect()


@pytest.fixture
async def send_message_u1_u2(socketio_client_w_auth_u1, user1, signup_user2_response) -> AsyncGenerator[
    Tuple[p.SioResponseSchema, str], None]:
    message_content = f'hello from user {user1.email}'
    user_to_id = signup_user2_response.json().get('id')
    assert user_to_id is not None
    res = await socketio_client_w_auth_u1.call('message', data={
        "contact_id": user_to_id,
        "content": message_content
    })
    yield p.SioResponseSchema(**res), message_content
