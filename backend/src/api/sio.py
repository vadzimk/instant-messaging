import logging
import os
from functools import wraps
from typing import Callable, Type

import socketio
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError

from src.api.dependencies import authenticated_user, get_current_user_id
from src.celery_app.tasks import send_telegram_notification
from src.db import models as m

from src import redis_client
from src import schemas as p
from src.db.session import Session
from src.services.message_service import MessageService
from src.settings import server_settings
from src.services.user_service import UserService
from src.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src import exceptions as e

logger = logging.getLogger(__name__)

redis_manager = socketio.AsyncRedisManager(
    url=f'redis://{server_settings.REDIS_HOST}:{server_settings.REDIS_PORT}/{server_settings.REDIS_DB}')

# test client https://github.com/serajhqi/socketio-test-client
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[],  # empty list to disable cors handling, bc fastapi cors middleware is in conflict
    client_manager=redis_manager
)

if os.getenv('ENV') == 'development':
    sio.instrument(auth=False, mode='development')  # only in development admin ui


# Validation decorator for both request and response
def validate(request_model: Type[BaseModel], response_model: Type[BaseModel]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(sid, data, *args, **kwargs):
            # Validate incoming data
            try:
                validated_data = request_model.model_validate(data)
            except ValidationError as err:
                return jsonable_encoder(p.SioResponseSchema(success=False, data=data, errors=err.errors()))

            # Execute the handler and get the response
            try:
                func_response = await func(sid, validated_data, *args, **kwargs)
            except Exception as exc:
                logger.error(exc)
                response = p.SioResponseSchema(success=False, data=None, errors=["Internal server error"])
                if isinstance(exc, e.UserNotFoundException):
                    response = p.SioResponseSchema(success=False, data=None, errors=[str(exc)])
                return jsonable_encoder(response)

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

    async with Session() as db_session:
        async with SqlAlchemyUnitOfWork(db_session) as uow:
            user_service = UserService(uow) # TODO replace with Depends(get_user_service)
            user: m.User = await authenticated_user(user_email, user_service)

            await sio.save_session(sid,
                                   {'user_id': user.id})  # is user_id retrieved from sio_session in other endpoints

            # store sid in redis by user_id
            # TODO if the client connects from second device the first device sid will be overridden
            #  and messages on the first device will not go through
            await redis_client.set_user_sid(user_id=user.id, sid=sid)
            user_sid_in_redis = await redis_client.get_user_sid(user.id)
            logger.info(f'Connected user.id: {user.id}, user_sid_in_redis: {user_sid_in_redis}')


@sio.event
@validate(p.CreateMessageSchema, p.GetMessageSchema)
async def message_send(sid, msg: p.CreateMessageSchema):
    """
    Event to send a message to another user in the chat,
    if user is online, he gets to listen on the event 'message_receive'
    if user is offline, he gets telegram notification if subscribed
    @param sid: The socket.io session id of the client of the user_from
    @param msg: payload form the client
    @return: p.GetMessageSchema
    """
    sio_session = await sio.get_session(sid)
    user_id_from = sio_session.get("user_id")
    async with Session() as db_session:
        async with SqlAlchemyUnitOfWork(db_session) as uow:
            message_service = MessageService(uow)
            saved_msg = await message_service.save_message(
                user_id_from=user_id_from,
                user_id_to=msg.contact_id,
                content=msg.content
            )

            # emit the event to user_to if he is online
            user_to__sid = await redis_client.get_user_sid(msg.contact_id)
            logger.info(f'Sending message to user_to.id: {msg.contact_id}, user_to__sid: {user_to__sid}')
            get_message_response = p.GetMessageSchema.model_validate(saved_msg)
            if user_to__sid:  # is online
                await sio.emit('message_receive',
                               data=jsonable_encoder(get_message_response),
                               to=user_to__sid,
                               # callback=lambda acknowledgment_data: logger.info(f'>>> message_receive event callback: {acknowledgment_data}')
                               )
                logger.info(f'Message sent to online user {user_to__sid}')
            else:  # user is offline
                user_service = UserService(uow)
                user_to = await user_service.get_existing_user({'id': msg.contact_id})
                user_from = await user_service.get_existing_user({'id': user_id_from})
                if not user_to:
                    raise e.UserNotFoundException(f'User with id {msg.contact_id} not found')
                content = f"New message from\n{user_from.first_name} {user_from.last_name} ({user_from.email})\n" \
                          f"{get_message_response.content}"

                celery_task = send_telegram_notification.delay(user_to.telegram_id, content)

        return get_message_response


# @sio.event
# async def message_receive_ack(sid, data):
#     logger.info(f'>>> Acknowledgment received from client: {data}')

@sio.event
async def disconnect(sid):
    sio_session = await sio.get_session(sid)
    user_id = sio_session.get('user_id')
    await redis_client.delete_user_sid(user_id)
    logger.info(f'Client {sid} disconnected')


@sio.event
async def ping(sid, data):
    logger.info(f'Client {sid}, data {data}')
    return data
