import logging
import os
from functools import wraps
from typing import Callable, Type

import socketio
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from sqlalchemy import select

from src.api.dependencies import get_user, get_current_user_id
from src.db import models as m

from src import redis_client
from src import schemas as p
from src.db.session import get_db, Session
from src.main import server_settings
from src.services.user_service import UserService
from src.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork

logger = logging.getLogger(__name__)

redis_manager = socketio.AsyncRedisManager(
    url=f'redis://{server_settings.REDIS_HOST}:{server_settings.REDIS_PORT}/0')

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
                return jsonable_encoder(p.SioResponseSchema(success=False, data=data, errors=e.errors()))

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
    user_email = get_current_user_id(token)

    async with Session() as session:
        async with SqlAlchemyUnitOfWork(session) as uow:
            user_service = UserService(uow)
            user: m.User = await get_user(user_email, user_service)

            await sio.save_session(sid, {'user_id': user.id})

            # store sid in redis by user_id
            # TODO if the client connects from second device the first device sid will be overridden
            #  and messages on the first device will not go through
            await redis_client.set_user_sid(user_id=user.id, sid=sid)
            user_sid_in_redis = await redis_client.get_user_sid(user.id)
            logger.info(f'on connection >>> {user.id} user_sid_in_redis {user_sid_in_redis}')


@sio.event
@validate(p.CreateMessageSchema, p.GetMessageSchema)
async def message_send(sid, msg: p.CreateMessageSchema):
    sio_session = await sio.get_session(sid)
    user_id_from = sio_session.get("user_id")
    async for db_session in get_db():
        user_from = await db_session.scalar(select(m.User).where(m.User.id == user_id_from))
        user_to = await db_session.scalar(select(m.User).where(m.User.id == msg.contact_id))
        msg = m.Message(user_from=user_from, user_to=user_to, content=msg.content)
        db_session.add(msg)
        await db_session.commit()

        # emit the event to user_to if he is online
        user_to__sid = await redis_client.get_user_sid(user_to.id)
        logger.info(f'>>> sending message to user_to.id {user_to.id} >>> user_to__sid {user_to__sid}')
        if user_to__sid:  # is online
            await sio.emit('message_receive',
                           data=jsonable_encoder(p.GetMessageSchema.model_validate(msg)),
                           to=user_to__sid,
                           # callback=lambda acknowledgment_data: logger.info(f'>>> message_receive event callback: {acknowledgment_data}')
                           )
        logger.info(f'>>> msg sent to {user_to__sid}')
        return p.GetMessageSchema.model_validate(msg)


# @sio.event
# async def message_receive_ack(sid, data):
#     logger.info(f'>>> Acknowledgment received from client: {data}')

@sio.event
async def disconnect(sid):
    msg = f'Client {sid} disconnected'
    logger.info(msg)


@sio.event
async def ping(sid, data):
    msg = f'Client {sid}, data {data}'
    logger.info(msg)
    return data
