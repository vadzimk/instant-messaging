from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.abstract_repository import AbstractRepository, T
from .. import models as m
from ..Exceptions import EntityNotFoundError


class UserRepository(AbstractRepository[m.User]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, entity: m.User) -> m.User:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get(self, filters: Dict[str, Any]) -> Optional[m.User]:
        result = await self.session.execute(select(m.User).filter_by(**filters))
        return result.scalars().first()

    async def update(self, filters: Dict[str, Any], update: Dict[str, Any]) -> Optional[T]:
        user = await self.get(filters)
        if not user:
            raise EntityNotFoundError(f'User matching filters not found {filters}')
        for key, value in update.items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, filters: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def list(
            self,
            cursor: Optional[Tuple[datetime, str | UUID]],
            limit: Optional[int],
            sort: Optional[List[Tuple[str]]] = None,
            filters: Optional[Dict[str, Any]] = None,
            *,
            dynamic_filters: Optional[List[Tuple[str, str, Any]]] = None
    ) -> List[m.User]:
        limit = limit if limit is not None else 10
        sort = sort if isinstance(sort, list) and len(sort) else [('created_at', 'asc'), ('id', 'asc')]

        q = select(m.User)
        ordering = [
            getattr(m.User, col).asc() if direction == 'asc' else getattr(m.User, col).desc()
            for col, direction in sort
        ]
        q = q.order_by(*ordering)
        if filters:
            q = q.filter_by(**filters)
        if dynamic_filters:
            dynamic_conditions = [
                getattr(getattr(m.User, column), operator)(value)  # creates sqlalchemy expression object
                for column, operator, value in dynamic_filters
            ]
            q = q.filter(and_(*dynamic_conditions))

        if cursor:
            cursor_datetime, cursor_id = cursor
            cursor_conditions = [
                (getattr(m.User, 'created_at') > cursor_datetime) |  # logical OR
                ((getattr(m.User, 'created_at') == cursor_datetime) & (getattr(m.User, 'id') > cursor_id))
            ]
            q.filter(and_(*cursor_conditions))
        q = q.limit(limit)
        return list((await self.session.execute(q)).scalars().all())
