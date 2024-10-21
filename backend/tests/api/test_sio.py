import asyncio

import pytest
import socketio


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
    assert sid is not None, "Expected connection to succeed with authentication, but it failed"


# @pytest.mark.only
async def test_foo_connect_fail_with_no_auth(socketio_client_no_auth):
    assert socketio_client_no_auth is None, "Expected connection to fail without authentication, but it succeeded "


@pytest.mark.only
async def test_ping(socketio_client_w_auth):
    data_to_send = 'hello'
    res = await socketio_client_w_auth.call('ping', data=data_to_send,
                                            timeout=2)  # to get ack, the call() method should be used
    assert res == data_to_send
