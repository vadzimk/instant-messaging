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

    async def save_message(self, user_id_from: UUID, user_id_to: UUID, content: str):
        user_repo = self._uow.get_user_repository()

        user_from = await user_repo.get({'id': user_id_from})
        user_to = await user_repo.get({'id': user_id_to})

        if not (user_from and user_to):
            NotImplementedError("Send error response in sio")
        msg = m.Message(user_from=user_from, user_to=user_to, content=content)
        msg = await self.message_repo.add(msg)
        await self._uow.commit()
        return msg
