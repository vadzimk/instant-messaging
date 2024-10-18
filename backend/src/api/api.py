from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette import status
from starlette.requests import Request

from ..services.auth import hash_password, verify_password, generate_jwt
from .schemas import *
from ..db import Session
from .. import models as m

router = APIRouter()


async def get_db():
    session = Session()
    try:
        yield session
    finally:
        await session.close()


@router.post('/signup', response_model=UserCreateOut, status_code=status.HTTP_201_CREATED)
async def signup_user(user: UserCreateIn, session: Session = Depends(get_db)):
    existing_user = await session.scalar(select(m.User).where(m.User.email == user.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = hash_password(user.password)
    new_user = m.User(email=user.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post('/login', response_model=UserLoginOut)
async def login_user(user_credentials: UserLoginIn, session: Session = Depends(get_db)):
    user = await session.scalar(select(m.User).where(m.User.email == user_credentials.email))
    if not (user and verify_password(user_credentials.password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = generate_jwt(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/me')
async def me(request: Request):
    user_email = request.state.user_id
    print("user_email", user_email)
