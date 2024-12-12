import logging
from typing import Optional, Dict, Any
from fastapi.security import OAuth2PasswordRequestForm
from src import exceptions as e
from src.services.auth import hash_password, verify_password, generate_jwt
from src.db import models as m
from src.repositories.repos import UserRepository
from src.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src import schemas as p

from src.logger import logger


# service classes can reference any repository that is why I do a commit inside service class itself
class UserService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self._uow = uow
        self._user_repo: Optional[UserRepository] = None

    @property
    def user_repo(self) -> UserRepository:
        if self._user_repo is None:
            self._user_repo = self._uow.get_user_repository()
        return self._user_repo

    async def get_existing_user(self, filters: Dict[str, Any]) -> Optional[m.User]:
        self._uow.mark_read_only()
        return await self.user_repo.get(filters)

    async def register_user(self, user_data: p.CreateUserSchema) -> m.User:

        existing_user = await self.user_repo.get({'email': user_data.email})
        if existing_user:
            raise e.AlreadyRegisteredException("Email already registered")
        hashed_password = hash_password(user_data.password)
        new_user = m.User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name)
        new_user = await self.user_repo.add(new_user)
        await self._uow.commit()
        return new_user

    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> p.LoginUserSchema:
        user_email = form_data.username
        user_password = form_data.password
        self._uow.mark_read_only()
        user = await self.user_repo.get({'email': user_email})
        if not (user and verify_password(user_password, user.hashed_password)):
            raise e.IncorrectCredentialsException("Incorrect username or password")
        access_token = generate_jwt(data={'sub': user.email})
        return p.LoginUserSchema(
            **user.dict(),
            access_token=access_token,
            token_type='bearer'
        )

    async def subscribe_notifications(self, user_data: p.SubscribeToNotifications):
        """ subscribes user to telegram notifications """
        try:
            res = await self.user_repo.update(
                filters={'email': user_data.user_email},
                update={'telegram_id': user_data.tg_user_id}
            )
            await self._uow.commit()
            logger.info(f'updated_user {res.telegram_id}')
        except e.EntityNotFoundError:
            raise e.UserNotFoundException(f'User with email: {user_data.user_email} does not exist')
