import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from starlette import status
from ..services.auth import hash_password, verify_password, generate_jwt, get_user
from . import schemas as p
from ..db import get_db
from .. import models as m

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/users', response_model=p.GetUserSchema, status_code=status.HTTP_201_CREATED)
async def signup_user(
        user: p.CreateUserSchema,
        session: AsyncSession = Depends(get_db)
):
    existing_user = await session.scalar(select(m.User).where(m.User.email == user.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = hash_password(user.password)
    new_user = m.User(email=user.email,
                      hashed_password=hashed_password,
                      first_name=user.first_name,
                      last_name=user.last_name)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post('/users/login', response_model=p.LoginUserSchema)
async def login_user(
        #  The OAuth2 specification for a password flow the data should be collected using form data (instead of JSON)
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_db)
):
    user_email = form_data.username
    user_password = form_data.password
    user = await session.scalar(select(m.User).where(m.User.email == user_email))
    if not (user and verify_password(user_password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = generate_jwt(data={'sub': user.email})
    return p.LoginUserSchema(
        **user.dict(),
        access_token=access_token,
        token_type='bearer'
    )


@router.post('/me')
async def me(user: p.GetUserSchema = Depends(get_user)):
    print("user_email", user.email)


@router.post('/contacts', response_model=p.GetContactSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(
        contact_fields: p.CreateContactSchema,
        user: p.GetUserSchema = Depends(get_user),
        session: AsyncSession = Depends(get_db)
):
    user1 = await session.scalar(select(m.User).where(m.User.email == user.email))
    user2 = await session.scalar(select(m.User).where(m.User.email == contact_fields.email))
    if not user2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f'User {contact_fields.email} not found')
    try:
        await session.execute(m.Contact.insert().values(user_id=user1.id, contact_id=user2.id))
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Contact already exists')
    return user2


@router.get('/contacts', response_model=p.GetContactsSchema)
async def get_contacts(
        user: p.GetUserSchema = Depends(get_user),
        session: AsyncSession = Depends(get_db)
):
    UserContact = aliased(m.User)
    q = (select(m.User, UserContact)
         .join(m.Contact, m.User.id == m.Contact.c.user_id)
         .join(UserContact, m.Contact.c.contact_id == UserContact.id)
         .where(m.User.email == user.email))
    result = (await session.execute(q)).all()
    contacts = [p.GetContactSchema.model_validate(c) for _, c in result]
    return p.GetContactsSchema(contacts=contacts)


@router.get('/chats/{contact_id}', response_model=p.GetMessagesSchema)
async def get_messages(
        contact_id: uuid.UUID,
        user: p.GetUserSchema = Depends(get_user),
        session: AsyncSession = Depends(get_db),
):
    user_from_alias = aliased(m.User)
    user_to_alias = aliased(m.User)
    q = (select(m.Message)
    .join(target=user_from_alias, onclause=m.Message.user_from)
    .join(target=user_to_alias, onclause=m.Message.user_to)
    .where(
        or_(m.Message.user_from.has(id=user.id) & m.Message.user_to.has(id=contact_id),
            m.Message.user_from.has(id=contact_id) & m.Message.user_to.has(id=user.id)
            )
    ))
    messages = [p.GetMessageSchema.model_validate(msg)
                for msg in (await session.scalars(q)).all()]
    return p.GetMessagesSchema(messages=messages)
