import os
from datetime import datetime, timedelta
from pathlib import Path

from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette import status
from cryptography.hazmat.primitives import serialization
import jwt
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


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_jwt(data):
    now = datetime.utcnow()
    payload = {
        "iss": "https://messaging.vadzimk.com",
        "sub": data.get('sub'),
        "aud": "http://127.0.0.1:8000/",
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=24)).timestamp(),
        "scope": "openid"
    }
    private_key_path = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / 'jwt_keys/private_key.pem'
    private_key_text = private_key_path.read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(encoding='utf-8'),  # utf-8 is default
        password=None
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")


@router.post('/register', response_model=UserCreateOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreateIn, session: Session = Depends(get_db)):
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
