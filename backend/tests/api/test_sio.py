from typing import Tuple, AsyncGenerator

import pytest
import socketio
from httpx import Response
from sqlalchemy import select, or_
from sqlalchemy.orm import aliased

from src.db import Session
from src import models as m


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
        await client.connect('http://localhost:8000')
    except socketio.exceptions.ConnectionError:
        client = None
    yield client
    if client:
        await client.disconnect()


# @pytest.mark.only
async def test_foo_connect_success_with_auth(socketio_client_w_auth_u1):
    sid = socketio_client_w_auth_u1.sid
    print(sid)
    assert sid is not None, "Expected socketio connection to succeed with authentication, but it failed"


# @pytest.mark.only
async def test_foo_connect_fail_with_no_auth(socketio_client_no_auth):
    assert socketio_client_no_auth is None, "Expected socketio connection to fail without authentication, but it succeeded "


async def test_ping(socketio_client_w_auth_u1):
    data_to_send = 'hello'
    res = await socketio_client_w_auth_u1.call('ping', data=data_to_send,
                                               timeout=2)  # to get ack, the call() method should be used
    assert res == data_to_send, "Socketio ping event handler did not send expected reply"


@pytest.fixture
async def send_message(socketio_client_w_auth_u1, user1, signup_user2_response) -> AsyncGenerator[Tuple[Response, str], None]:
    message_content = f'hello from user {user1.email}'
    user_to_email = signup_user2_response.json().get('email')
    res = await socketio_client_w_auth_u1.call('message', data={
        "to": user_to_email,
        "content": message_content
    })
    yield res, message_content


# @pytest.mark.only
async def test_message(send_message, user1, user2):
    res, expected_content = send_message
    # checks if message is in database
    async with Session() as session:
        async with session.begin():
            u_from = await session.scalar(select(m.User).where(m.User.email == user1.email))
            u_to = await session.scalar(select(m.User).where(m.User.email == user2.email))
            user_from_alias = aliased(m.User)
            user_to_alias = aliased(m.User)
            q = select(m.Message.content, user_from_alias.email, user_to_alias.email) \
                .join(target=user_from_alias, onclause=m.Message.user_from) \
                .join(target=user_to_alias, onclause=m.Message.user_to) \
                .where(
                or_(
                    (m.Message.user_from == u_from) & (m.Message.user_to == u_to),
                    (m.Message.user_from == u_to) & (m.Message.user_to == u_from)
                ))
            r = await session.execute(q)
            result = r.all()
            assert result == [(expected_content,
                               user1.email,
                               user2.email)], "Message from user1 to user2 was not sent successfully"
