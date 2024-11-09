import logging
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.repos import UserRepository, MessageRepository, ContactRepository

logger = logging.getLogger(__name__)


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


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._committed = False
        self._read_only = False
        self._user_repository = UserRepository(self._session)
        self._message_repository = MessageRepository(self._session)
        self._contact_repository = ContactRepository(self._session)

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        if not self._committed and not self._read_only:
            logger.warning(f"{self.__class__.__name__} exited without a commit")

    async def commit(self):
        self._committed = True
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    def get_user_repository(self) -> UserRepository:
        return self._user_repository

    def get_message_repository(self) -> MessageRepository:
        return self._message_repository

    def get_contact_repository(self) -> ContactRepository:
        return self._contact_repository

    def mark_read_only(self):
        """
        guards against uncommitted updates
        commit must be done in client code when read_only is False
        usage: inside service method before database operation call this method if db operation is not making changes to the database,
            this will prevent logging a warning when uow is exited without a commit
        """
        self._read_only = True
