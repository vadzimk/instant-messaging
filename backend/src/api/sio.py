import logging
import socketio
from sqlalchemy import select

from ..db import get_db
from ..services.auth import get_current_user_id, get_user
from .. import models as m

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
    sio_session = await sio.get_session(sid)
    user_email_from = sio_session.get("username")
    user_email_to = data.get("to")
    content = data.get("content")
    async for db_session in get_db():
        user_from = await db_session.scalar(select(m.User).where(m.User.email==user_email_from))
        user_to = await db_session.scalar(select(m.User).where(m.User.email==user_email_to))
        msg = m.Message(user_from=user_from, user_to=user_to, content=content)
        db_session.add(msg)
        await db_session.commit()
    return f'Msg from: {user_from.email} to: {user_to.email} content: {content}'


@sio.event
async def disconnect(sid):
    msg = f'Client {sid} disconnected'
    logger.info(msg)


@sio.event
async def ping(sid, data):
    msg = f'Client {sid}, data {data}'
    logger.info(msg)
    return data
