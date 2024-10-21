import logging
import socketio

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
    msg = f'Client {sid} connected, environ {environ}, auth {auth}'
    logger.info(msg)


@sio.event
async def disconnect(sid):
    msg = f'Client {sid} disconnected'
    logger.info(msg)


@sio.event
async def foo(sid, data):
    msg = f'Client {sid}, data {data}'
    logger.info(msg)
    return f'bar-{data.get("body")}'

def message(sid, data):
    pass

