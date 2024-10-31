from typing import Tuple, List
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.repositories.abstract_repository import AbstractRepository
from src.db import models as m


class UserRepository(AbstractRepository[m.User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, m.User)


class ContactRepository(AbstractRepository[m.Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, m.Contact)

    async def list_user_contacts(self, existing_user: m.User) -> List[Tuple[m.Contact, m.User]]:
        """
        @return: list of tuples: [(m.Contact, m.User)] of existing user
        """
        UserContact = aliased(m.User)
        q = (select(m.Contact, UserContact)
             .join(m.Contact.user)
             .join(UserContact, m.Contact.contact_user)
             .where(m.User.id == existing_user.id))

        return list((await self.session.execute(q)).all())


class MessageRepository(AbstractRepository[m.Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, m.Message)

    async def list_messages(self, existing_user: m.User, contact_id: UUID) -> List[m.Message]:
        # TODO pagination
        user_from_alias = aliased(m.User)
        user_to_alias = aliased(m.User)
        q = (select(m.Message)
        .join(target=user_from_alias, onclause=m.Message.user_from)
        .join(target=user_to_alias, onclause=m.Message.user_to)
        .where(
            or_(m.Message.user_from.has(id=existing_user.id) & m.Message.user_to.has(id=contact_id),
                m.Message.user_from.has(id=contact_id) & m.Message.user_to.has(id=existing_user.id)
                )
        ))
        return list((await self.session.scalars(q)).all())
