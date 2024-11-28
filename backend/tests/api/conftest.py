import os
from asyncio import Future
from typing import AsyncGenerator, Tuple
import pytest
import asyncio

import pytest_asyncio
from httpx import AsyncClient, ASGITransport, Response
from sqlalchemy import select
from pathlib import Path
from cryptography.x509 import load_pem_x509_certificate
import socketio
import jwt

from src.main import app
from src.db.session import Session
from src.db import models as m
from src import schemas as p
from tests.data.data import user1, user2, baseUrl


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def httpx_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client
        # automatically handles disconnect


# this is not a fixture
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


# this is not a fixture
async def signup_user(user: p.CreateUserSchema) -> AsyncGenerator[Response, None]:
    signup_res_iterator = signup_user_helper(user)
    signup_res = await anext(signup_res_iterator)
    yield signup_res
    try:
        await anext(signup_res_iterator)  # cleanup
    except StopAsyncIteration:
        pass  # expected


@pytest.fixture
async def signup_user1_response() -> AsyncGenerator[Response, None]:
    """ deletes user after test run """
    async for response in signup_user(user1):  # use loop instead of yield from, async yield from not supported
        yield response


@pytest.fixture
async def signup_user2_response() -> AsyncGenerator[Response, None]:
    """ deletes user after test run """
    async for response in signup_user(user2):  # use loop instead of yield from, async yield from not supported
        yield response


@pytest.fixture
async def login_user1_response(signup_user1_response, httpx_client) -> AsyncGenerator[Response, None]:
    yield await httpx_client.post(
        '/api/users/login', data={  # send as form data
            'username': user1.email,
            'password': user1.password
        })


@pytest.fixture
async def login_user2_response(signup_user2_response, httpx_client) -> AsyncGenerator[Response, None]:
    yield await httpx_client.post(
        '/api/users/login', data={  # send as form data
            'username': user2.email,
            'password': user2.password
        })


def decode_access_token(access_token) -> str:
    # validate token on the client for each request
    if os.getenv('ENV') == 'development':
        public_key_path = Path(__file__).parent.parent.parent / 'jwt_keys/public_key.pem'
        public_key_text = public_key_path.read_text()
    else:
        public_key_text = os.getenv('JWT_PUBLIC_KEY')
    public_key = load_pem_x509_certificate(public_key_text.encode('utf-8')).public_key()
    validated_result_payload = jwt.decode(
        access_token,
        key=public_key,
        algorithms=['RS256'],
        audience=[os.getenv('JWT_AUDIENCE')])
    return validated_result_payload


@pytest.fixture
async def client_with_auth_user1(login_user1_response, httpx_client) -> AsyncGenerator[AsyncClient, None]:
    httpx_client.headers.update({
        'Authorization': f'Bearer {login_user1_response.json().get("access_token")}'
    })
    yield httpx_client


@pytest.fixture
async def create_u2_contact_for_u1_response(client_with_auth_user1, signup_user2_response):
    new_contact = p.CreateContactSchema(**signup_user2_response.json())
    return await client_with_auth_user1.post(
        '/api/contacts',
        json=new_contact.model_dump()
    )


@pytest.fixture
async def socketio_client_w_auth_u1(login_user1_response) -> AsyncGenerator[socketio.AsyncSimpleClient, None]:
    access_token = login_user1_response.json().get("access_token")
    client = socketio.AsyncSimpleClient()
    await client.connect(baseUrl, auth={"token": access_token})
    yield client
    await client.disconnect()


@pytest.fixture
async def socketio_client_w_auth_u2(login_user2_response) -> AsyncGenerator[socketio.AsyncClient, None]:
    access_token = login_user2_response.json().get("access_token")
    client = socketio.AsyncClient(
        logger=True, engineio_logger=True
    )
    await client.connect(baseUrl, auth={"token": access_token})
    print(f'>>> client of user2 connected, sid {client.get_sid()}')
    yield client
    await client.disconnect()


@pytest.fixture
async def socketio_client_u2_receive_message_future(socketio_client_w_auth_u2) -> AsyncGenerator[Future, None]:
    future = asyncio.get_running_loop().create_future()  # https://github.com/miguelgrinberg/python-socketio/issues/332#issuecomment-712928157

    @socketio_client_w_auth_u2.on('message_receive')
    async def message_receive(data):
        print(f'>>> received message {data}')
        # # Send acknowledgment data back to the server
        # acknowledgment_data = {'status': 'received', 'data_id': data.get('id')}
        # await client.emit('message_receive_ack', acknowledgment_data)
        future.set_result(data)

    print('>>> client waiting')
    yield future


@pytest.fixture
async def socketio_client_no_auth() -> AsyncGenerator[socketio.AsyncSimpleClient, None]:
    client = socketio.AsyncSimpleClient()
    try:
        await client.connect(baseUrl, wait_timeout=2)
    except socketio.exceptions.ConnectionError:
        client = None
    yield client
    if client:
        await client.disconnect()


@pytest.fixture
async def send_message_u1_u2(socketio_client_w_auth_u1, signup_user2_response) -> AsyncGenerator[
    Tuple[p.SioResponseSchema, str], None]:
    message_content = f'hello from user {user1.email}'
    user_to_id = signup_user2_response.json().get('id')
    assert user_to_id is not None
    res = await socketio_client_w_auth_u1.call('message_send', data={
        "contact_id": user_to_id,
        "content": message_content
    })
    print('>>> message sent from user1 to user2')
    yield p.SioResponseSchema(**res), message_content
