from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette import status

from .schemas import UserCreate
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


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, session: Session = Depends(get_db)):
    existing_user = await session.scalar(select(m.User).where(m.User.email == user.email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    new_user = m.User(email=user.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"msg": "User registered successfully"}
