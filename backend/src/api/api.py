import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from starlette import status

from src.api.dependencies import (
    authenticated_user, UserServiceDep, ContactServiceDep, MessageServiceDep)

from src.db import models as m
from src import schemas as p

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/users', response_model=p.GetUserSchema, status_code=status.HTTP_201_CREATED)
async def signup_user(
        user: p.CreateUserSchema,
        user_service: UserServiceDep
):
    return await user_service.register_user(user)


@router.post('/users/login', response_model=p.LoginUserSchema)
async def login_user(
        #  The OAuth2 specification for a password flow the data should be collected using form data (instead of JSON)
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: UserServiceDep
):
    return await user_service.login_user(form_data)


@router.post('/me')
async def me(user: m.User = Depends(authenticated_user)):
    print("user_email", user.email)


@router.post('/contacts', response_model=p.GetContactSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(
        contact_fields: p.CreateContactSchema,
        contact_service: ContactServiceDep,
        user: m.User = Depends(authenticated_user)
):
    return await contact_service.add_contact(user, contact_fields)


@router.get('/contacts', response_model=p.GetContactsSchema)
async def get_contacts(
        contact_service: ContactServiceDep,
        user: m.User = Depends(authenticated_user),
):
    return p.GetContactsSchema(contacts=[
        p.GetContactSchema.model_validate(c)
        for c in await contact_service.list_contacts(user)]
    )


@router.get('/chats/{contact_id}', response_model=p.GetMessagesSchema)
async def get_messages(
        contact_id: uuid.UUID,
        message_service: MessageServiceDep,
        user: m.User = Depends(authenticated_user),
):
    return p.GetMessagesSchema(messages=[
        p.GetMessageSchema.model_validate(msg)
        for msg in await message_service.list_messages(user, contact_id)
    ])
