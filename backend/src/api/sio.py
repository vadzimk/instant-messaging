import logging
import socketio

from ..db import get_db
from ..services.auth import get_current_user_id, get_user

logger = logging.getLogger(__name__)

redis_manager = socketio.AsyncRedisManager(url='redis://localhost:6379/0')
# test client https://github.com/serajhqi/socketio-test-client
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[],  # empty list to disable cors handling, bc fastapi cors middleware is in conflict
    client_manager=redis_manager
)
sio.instrument(auth=False, mode='development')  # only in development admin ui


@sio.event
async def connect(sid, environ, auth):
    if not auth:
        raise socketio.exceptions.ConnectionRefusedError('Socketio Authentication failed')
    token = auth.get('token')
    # logger.info(f'token {token}')
    user_email = get_current_user_id(token)
    # logger.info(f'user_email {user_email}')
    async for session in get_db():  # consume async generator
        user = await get_user(user_email, session)
    username = user.email
    await sio.save_session(sid, {'username': username})
    # logger.info(f'sid: {sid}, auth: {auth}, username: {username}')


@sio.event
async def message(sid, data):
    session = await sio.get_session(sid)
    return f'your username: {session.get("username")}'


@sio.event
async def disconnect(sid):
    msg = f'Client {sid} disconnected'
    logger.info(msg)


@sio.event
async def ping(sid, data):
    msg = f'Client {sid}, data {data}'
    logger.info(msg)
    return data
