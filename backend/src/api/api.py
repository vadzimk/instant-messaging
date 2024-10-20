from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette import status
from ..services.auth import hash_password, verify_password, generate_jwt, get_user
from . import schemas as p
from ..db import Session, get_db
from .. import models as m

router = APIRouter()


@router.post('/signup', response_model=p.UserCreateOut, status_code=status.HTTP_201_CREATED)
async def signup_user(user: p.UserCreateIn, session: Session = Depends(get_db)):
    existing_user = await session.scalar(select(m.User).where(m.User.email == user.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = hash_password(user.password)
    new_user = m.User(email=user.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post('/login', response_model=p.UserLoginOut)
async def login_user(user_credentials: p.UserLoginIn, session: Session = Depends(get_db)):
    user = await session.scalar(select(m.User).where(m.User.email == user_credentials.email))
    if not (user and verify_password(user_credentials.password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = generate_jwt(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/me')
async def me(user: p.User = Depends(get_user)):
    print("user_email", user.email)
