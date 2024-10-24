import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from ..services.auth import hash_password, verify_password, generate_jwt, get_user
from . import schemas as p
from ..db import get_db
from .. import models as m

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/signup', response_model=p.UserSignupOut, status_code=status.HTTP_201_CREATED)
async def signup_user(user: p.UserSignupIn, session: AsyncSession = Depends(get_db)):
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


@router.post('/login', response_model=p.UserLoginOut)
async def login_user(
        #  The OAuth2 specification for a password flow the data should be collected using form data (instead of JSON)
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_db)):
    user_email = form_data.username
    user_password = form_data.password
    user = await session.scalar(select(m.User).where(m.User.email == user_email))
    if not (user and verify_password(user_password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = generate_jwt(data={'sub': user.email})
    return p.UserLoginOut(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        access_token=access_token,
        token_type='bearer'
    )


@router.post('/me')
async def me(user: p.User = Depends(get_user)):
    print("user_email", user.email)


@router.post('/add-contact', response_model=p.AddContactOut, status_code=status.HTTP_201_CREATED)
async def add_contact(contact_fields: p.AddContactIn,
                      user: p.User = Depends(get_user),
                      session: AsyncSession = Depends(get_db)):
    user1 = await session.scalar(select(m.User).where(m.User.email == user.email))
    user2 = await session.scalar(select(m.User).where(m.User.email == contact_fields.email))
    if not user2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'User {contact_fields.email} not found')
    try:
        await session.execute(m.Contact.insert().values(user_id=user1.id, contact_id=user2.id))
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Contact already exists')
    return p.AddContactOut(**user2.dict())
