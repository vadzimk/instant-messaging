from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.repos import UserRepository, MessageRepository, ContactRepository


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

    def get_contact_repository(self) -> ContactRepository:
        raise NotImplementedError()


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(self.session)
        self.message_repository = MessageRepository(self.session)
        self.contact_repository = ContactRepository(self.session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    def get_user_repository(self) -> UserRepository:
        return self.user_repository

    def get_message_repository(self) -> MessageRepository:
        return self.message_repository

    def get_contact_repository(self) -> ContactRepository:
        return self.contact_repository
