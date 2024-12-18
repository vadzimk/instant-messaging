import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from sqlalchemy import select, or_
from sqlalchemy.orm import aliased

from src.api.sio import message_send
from src.db import models as m
from src import schemas as p
from src.db.session import Session
from tests.data.data import user1, user2


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


async def test_message_send(send_message_u1_u2):
    res, expected_content = send_message_u1_u2
    # get_message_res = p.GetMessageSchema.model_validate(res.json())
    print("res", res)
    assert res.success, "socket.io event handler failed"
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


async def test_message_receive(socketio_client_u2_receive_message_future, send_message_u1_u2):
    _, expected_content = send_message_u1_u2
    await asyncio.wait_for(socketio_client_u2_receive_message_future, timeout=2)
    data = socketio_client_u2_receive_message_future.result()
    print(f'>>> data_received {data}')
    assert data.get("content") == expected_content


# this test will give a warning that the event loop was not properly closed because it uses message_send from the actual fastapi app
@pytest.mark.filterwarnings('ignore')
async def test_message_send_when_user_offline_calls_celery_task(signup_user1_response, signup_user2_response,
                                                                send_message_u1_u2):
    with patch('src.celery_app.tasks.send_telegram_notification.delay') as mock_send_telegram:
        user_from_id = signup_user1_response.json().get('id')
        user_to_id = signup_user2_response.json().get('id')
        user_to_telegram_id_expected = signup_user2_response.json().get('telegram_id')
        # create mock sio_session with predefined user id
        sio_session_mock = MagicMock()
        sio_session_mock.get.return_value = user_from_id

        # mock sio.get_session to return the mock sio_session_mock
        with patch('src.api.sio.sio.get_session', AsyncMock(return_value=sio_session_mock)):
            msg = p.CreateMessageSchema(
                contact_id=user_to_id,
                content='hello from me'
            )
            result = await message_send('sid', msg)

            mock_send_telegram.assert_called_once()
            called_args, _ = mock_send_telegram.call_args
            print("call args", mock_send_telegram.call_args)
            assert called_args[0] == user_to_telegram_id_expected or called_args[0] is None, \
                "User to telegram id must match but it did not"
