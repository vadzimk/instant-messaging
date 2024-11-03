import os
from uuid import UUID

import redis.asyncio as aioredis

rclient = aioredis.from_url(f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/0')


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
