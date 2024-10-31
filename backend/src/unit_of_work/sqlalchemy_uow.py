from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.message_repository import MessageRepository
from src.repositories.user_repository import UserRepository


class AbstractUnitOfWork(ABC):

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError()

    @abstractmethod
    async def commit(self):
        """ called by the client code """
        raise NotImplementedError()

    @abstractmethod
    def get_user_repository(self) -> UserRepository:
        raise NotImplementedError()

    @abstractmethod
    def get_message_repository(self) -> MessageRepository:
        raise NotImplementedError()


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(self.session)
        self.message_repository = MessageRepository(self.session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    def get_user_repository(self) -> UserRepository:
        return self.user_repository

    def get_message_repository(self) -> MessageRepository:
        return self.message_repository
