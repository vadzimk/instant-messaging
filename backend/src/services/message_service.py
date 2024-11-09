from typing import Optional, List
from uuid import UUID

from src.repositories.repos import MessageRepository
from src.unit_of_work.sqlalchemy_uow import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from src.db import models as m


class MessageService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self._uow = uow
        self._message_repo: Optional[MessageRepository] = None

    @property
    def message_repo(self) -> MessageRepository:
        if self._message_repo is None:
            self._message_repo = self._uow.get_message_repository()
        return self._message_repo

    async def list_messages(self, current_user: m.User, contact_id: UUID) -> List[m.Message]:
        self._uow.mark_read_only()
        return await self.message_repo.list_messages(current_user, contact_id)
