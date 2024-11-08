import aiohttp

API_BASE_URL = 'http://localhost:8000'


class NotificationService:
    @classmethod
    async def subscribe_user(cls, tg_user_id: int, user_email: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_BASE_URL, json={}) as res:
                data = await res.json()
                if res.status == 200:
                    return True
                else:
                    return False
