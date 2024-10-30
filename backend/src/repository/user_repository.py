from typing import Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.abstract_repository import AbstractRepository
from .. import models as m


class UserRepository(AbstractRepository[m.User]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, entity: m.User) -> m.User:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get(self, filters: Dict[str, Any]) -> Optional[m.User]:
        conditions = []
        for key, value in filters.items():
            conditions.append(
                getattr(m.User, key) == value  # creates SQLAlchemy expression object
            )
        return await self.session.scalar(select(m.User).where(*conditions))




