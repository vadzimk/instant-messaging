import asyncio

import pytest
import socketio

@pytest.fixture
async def socketio_client():
    client = socketio.AsyncClient()
    await client.connect('http://localhost:8000')
    yield client
    await client.disconnect()


# @pytest.mark.only
async def test_foo(socketio_client):
    @socketio_client.on('foo')
    async def handle_foo(data):
        assert data == 'bar'
    await socketio_client.emit('foo', data='hello')
