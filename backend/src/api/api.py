import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from starlette import status
from ..services.auth import hash_password, verify_password, generate_jwt, get_user
from . import schemas as p
from ..db import Session, get_db
from .. import models as m

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/signup', response_model=p.UserCreateOut, status_code=status.HTTP_201_CREATED)
async def signup_user(user: p.UserCreateIn, session: Session = Depends(get_db)):
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
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],  # for swagger ui
        user_credentials: Optional[p.UserLoginIn] = None,  # for the app
        session: Session = Depends(get_db)):
    user_email = None
    user_password = None
    if user_credentials:
        user_email = user_credentials.email
        user_password = user_credentials.password
    elif form_data.username and form_data.password:
        user_email = form_data.username
        user_password = form_data.password
    user = await session.scalar(select(m.User).where(m.User.email == user_email))
    if not (user and verify_password(user_password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = generate_jwt(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/me')
async def me(user: p.User = Depends(get_user)):
    print("user_email", user.email)
