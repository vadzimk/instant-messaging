import logging
from functools import wraps
from typing import Callable, Type

import socketio
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from sqlalchemy import select

from ..db import get_db
from ..services.auth import get_current_user_id, get_user
from .. import models as m
from . import schemas as p

logger = logging.getLogger(__name__)

redis_manager = socketio.AsyncRedisManager(url='redis://localhost:6379/0')
# test client https://github.com/serajhqi/socketio-test-client
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[],  # empty list to disable cors handling, bc fastapi cors middleware is in conflict
    client_manager=redis_manager
)
sio.instrument(auth=False, mode='development')  # only in development admin ui


# Validation decorator for both request and response
def validate(request_model: Type[BaseModel], response_model: Type[BaseModel]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(sid, data, *args, **kwargs):
            # Validate incoming data
            try:
                validated_data = request_model.model_validate(data)
            except ValidationError as e:
                return p.SioResponseSchema(success=False, data=data, errors=e.errors())

            # Execute the handler and get the response
            func_response = await func(sid, validated_data, *args, **kwargs)

            # Validate the response data before sending it to the client
            if not isinstance(func_response, response_model):
                validated_response = response_model.model_validate(func_response)
            else:
                validated_response = func_response
            response = p.SioResponseSchema(data=validated_response)
            serialized_response = jsonable_encoder(response)
            return serialized_response

        return wrapper

    return decorator


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
        await sio.save_session(sid, {'user_id': user.id})
    # logger.info(f'sid: {sid}, auth: {auth}, username: {username}')


@sio.event
@validate(p.CreateMessageSchema, p.GetMessageSchema)
async def message(sid, msg: p.CreateMessageSchema):
    sio_session = await sio.get_session(sid)
    user_id_from = sio_session.get("user_id")
    async for db_session in get_db():
        user_from = await db_session.scalar(select(m.User).where(m.User.id == user_id_from))
        user_to = await db_session.scalar(select(m.User).where(m.User.id == msg.contact_id))
        msg = m.Message(user_from=user_from, user_to=user_to, content=msg.content)
        db_session.add(msg)
        await db_session.commit()
        # return f'Msg from: {user_from.email} to: {user_to.email} content: {msg.content}'
        return p.GetMessageSchema.model_validate(msg)



@sio.event
async def disconnect(sid):
    msg = f'Client {sid} disconnected'
    logger.info(msg)


@sio.event
async def ping(sid, data):
    msg = f'Client {sid}, data {data}'
    logger.info(msg)
    return data
