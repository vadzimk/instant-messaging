from src.api.dependencies.auth import hash_password
from src.db import models as m
from src.unit_of_work.sqlalchemy_uow import AbstractUnitOfWork
from src import schemas as p
from starlette import status
from fastapi import HTTPException


class UserService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def register_user(self, user_data: p.CreateUserSchema):
        user_repo = self.uow.get_user_repository()
        existing_user = await user_repo.get({'email': user_data.email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        hashed_password = hash_password(user_data.password)
        new_user = m.User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name)
        await user_repo.add(new_user)
        await self.uow.commit() # commit transaction
        return new_user
