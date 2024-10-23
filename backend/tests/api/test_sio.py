from http.client import HTTPResponse
from typing import Tuple

import pytest
import socketio
from sqlalchemy import select, or_
from sqlalchemy.orm import aliased

from src.db import Session
from src import models as m
from src.api.schemas import UserCreateIn

from .conftest import signup_user_helper


@pytest.fixture
async def socketio_client_w_auth(login_user_response):
    access_token = login_user_response.json().get("access_token")
    client = socketio.AsyncSimpleClient()
    await client.connect('http://localhost:8000', auth={"token": access_token})
    yield client
    await client.disconnect()


@pytest.fixture
async def socketio_client_no_auth() -> socketio.AsyncClient:
    client = socketio.AsyncClient()
    try:
        await client.connect('http://localhost:8000')
    except socketio.exceptions.ConnectionError:
        client = None
    yield client
    if client:
        await client.disconnect()


# @pytest.mark.only
async def test_foo_connect_success_with_auth(socketio_client_w_auth):
    sid = socketio_client_w_auth.sid
    print(sid)
    assert sid is not None, "Expected socketio connection to succeed with authentication, but it failed"


# @pytest.mark.only
async def test_foo_connect_fail_with_no_auth(socketio_client_no_auth):
    assert socketio_client_no_auth is None, "Expected socketio connection to fail without authentication, but it succeeded "


async def test_ping(socketio_client_w_auth):
    data_to_send = 'hello'
    res = await socketio_client_w_auth.call('ping', data=data_to_send,
                                            timeout=2)  # to get ack, the call() method should be used
    assert res == data_to_send, "Socketio ping event handler did not send expected reply"


@pytest.fixture
async def send_message(socketio_client_w_auth, user) -> Tuple[HTTPResponse, UserCreateIn, str]:
    message_content = f'hello from user {user.email}'
    user2_to_data = UserCreateIn(
        email="user2@mail.com",
        first_name="user2",
        last_name="",
        password="secret"
    )
    signup_res_iterator = signup_user_helper(user2_to_data)
    signup_res = await anext(signup_res_iterator)
    user_to_email = signup_res.json().get('email')
    res = await socketio_client_w_auth.call('message', data={
        "to": user_to_email,
        "content": message_content
    })
    yield res, user2_to_data, message_content
    try:
        await anext(signup_res_iterator)  # cleanup created user
    except StopAsyncIteration:
        pass  # expected


# @pytest.mark.only
async def test_message(send_message, user):
    # checks if message is in database
    user2_email = send_message[1].email
    async with (Session() as session):
        async with session.begin():
            u_from = await session.scalar(select(m.User).where(m.User.email == user.email))
            u_to = await session.scalar(select(m.User).where(m.User.email == user2_email))
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
            assert result == [(send_message[2],
                               user.email,
                               send_message[1].email)], "Message from user1 to user2 was not sent successfully"
