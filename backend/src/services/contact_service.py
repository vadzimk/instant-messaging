import logging
from typing import Optional, List

from src.exceptions import IntegrityErrorException, UserNotFoundException
from src.repositories.repos import ContactRepository
from src.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src import schemas as p
from src.db import models as m

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self._uow = uow
        self._contact_repo: Optional[ContactRepository] = None

    @property
    def contact_repo(self) -> ContactRepository:
        if self._contact_repo is None:
            self._contact_repo = self._uow.get_contact_repository()
        return self._contact_repo

    async def add_contact(self, current_user: m.User, contact_fields: p.CreateContactSchema) -> m.User:
        user_repo = self._uow.get_user_repository()
        candidate_contact = await user_repo.get({'email': contact_fields.email})
        if not candidate_contact:
            raise UserNotFoundException(f'User {contact_fields.email} not found')

        contact = m.Contact(user=current_user, contact_user=candidate_contact)

        try:
            await self.contact_repo.add(contact)
            await self._uow.commit()
        except IntegrityErrorException as e:
            logging.error(f'Integrity error occurred {str(e)}')
            await self._uow.rollback()
            raise
        return candidate_contact

    async def list_contacts(self, current_user: m.User) -> List[m.User]:
        self._uow.mark_read_only()
        result = await self.contact_repo.list_user_contacts(current_user)
        return [user_contact for _, user_contact in result]
