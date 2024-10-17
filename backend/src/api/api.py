from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette import status

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


@router.post('/register', response_model=UserCreateOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreateIn, session: Session = Depends(get_db)):
    existing_user = await session.scalar(select(m.User).where(m.User.email == user.email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    new_user = m.User(email=user.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
