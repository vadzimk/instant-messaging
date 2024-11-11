import logging

import aiohttp

logger = logging.getLogger(__name__)

API_BASE_URL = 'http://localhost:8000/service/telegram'


class NotificationService:
    @classmethod
    async def subscribe_user(cls, tg_user_id: int, user_email: str) -> str:
        user_data = {'tg_user_id': tg_user_id, 'user_email': user_email}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_BASE_URL + '/subscriptions', json=user_data) as res:
                    if res.status == 204:
                        return "You've subscribed to message notifications"
                    else:
                        logger.error(f'Failed to subscribe. Status code: {res.status}. Response: {await res.json()}')
                        return f"Failed to subscribe\n{f'User with email: {user_email} does not exist' if res.status == 404 else (await res.json()).get('detail')}\nUse /start to try again to register for notifications"
        except aiohttp.ClientError as e:
            logger.error(f'Error wile subscribing user: {str(e)}')
            return "Failed to subscribe\nInternal server error"
