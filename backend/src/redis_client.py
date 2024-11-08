import os
from uuid import UUID

import redis.asyncio as aioredis

from src.main import server_settings

rclient = aioredis.from_url(
    f'redis://{server_settings.REDIS_HOST}:{server_settings.REDIS_PORT}/0')


async def set_user_sid(user_id: str | UUID, sid: str):
    await rclient.set(f'user:{str(user_id)}:sid', sid)


async def get_user_sid(user_id: str | UUID):
    binary_sid: bytes = await rclient.get(
        f'user:{str(user_id)}:sid')  # comes out as binary string (bytes object) from redis
    if not binary_sid:
        return None
    return binary_sid.decode('utf-8')


async def delete_user_sid(user_id: str | UUID):
    await rclient.delete(f'user:{str(user_id)}:sid')
