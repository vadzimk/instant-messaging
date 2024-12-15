from unittest.mock import patch

import pytest

from src.main import server


@pytest.fixture
async def cli(aiohttp_client):
    return await aiohttp_client(server.web_app)


async def test_notification_handler_can_send_message(cli):
    test_data = {
        'tg_user_id': 123,
        'content': 'Hello, this is a test message'
    }

    with patch('src.main.server.bot.send_message') as mock_send_message:
        mock_send_message.return_value = None  # will return None
        response = await cli.post('/notification', json=test_data)

        assert response.status == 204, f'/notification failed with status {response.status}'

        # verify mock was called with proper args
        mock_send_message.assert_called_once_with(chat_id=test_data['tg_user_id'], text=test_data['content'])
