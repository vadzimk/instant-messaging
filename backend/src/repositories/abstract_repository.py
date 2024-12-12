from datetime import datetime
from typing import TypeVar, Generic, Dict, Any, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import EntityNotFoundError, IntegrityErrorException

from src.logger import logger

T = TypeVar('T')


class AbstractRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: T):
        self.session = session
        self.model = model

    async def _save(self, entity: T) -> T:
        """ Helper method to flush and refresh and handle IntegrityError """
        try:
            await self.session.flush()
            await self.session.refresh(entity)
            # commit must be done in client code (service class) when using UOW pattern
            # example: class Service: ... def method(): ... self.uow.commit()
        except IntegrityError as err:
            raise IntegrityErrorException(f"Integrity constraint violated {str(err)}")
        return entity

    async def add(self, entity: T) -> T:
        """
        Inserts new row with entity into the session
        @param entity:
        @return: instance of inserted entity added to the session
        """
        self.session.add(entity)
        return await self._save(entity)

    async def get(self, filters: Dict[str, Any]) -> Optional[T]:
        """
        Retrieves first result or None
        @param filters: dictionary with key as entity attribute and value as equality condition
        @return: first result
        """
        result = await self.session.execute(select(self.model).filter_by(**filters))
        return result.scalars().first()

    async def update(self, filters: Dict[str, Any], update: Dict[str, Any]) -> Optional[T]:
        """
        Updates orm entity and returns updated instance in the session
        @param filters: dict of column value for where equality condition
        @param update: dict of new column value
        @return: updated entity in the session
        """
        entity = await self.get(filters)
        if not entity:
            raise EntityNotFoundError(f'Not found {self.model} matching filters {filters}')
        for col, value in update.items():
            setattr(entity, col, value)
        return await self._save(entity)

    async def delete(self, filters: Dict[str, Any]) -> None:
        entity = await self.get(filters)
        if entity:
            await self.session.delete(entity)
            await self.session.commit()

    async def list(
            self,
            cursor: Optional[Tuple[datetime, str | UUID]] = None,
            limit: Optional[int] = 10,
            sort: Optional[List[Tuple[str, str]]] = None,
            filters: Optional[Dict[str, Any]] = None,
            *,
            dynamic_filters: Optional[List[Tuple[str, str, Any]]] = None
    ) -> List[Any]:
        """
        Retrieves a paginated, filtered, and sorted list of items starting from a cursor position.
        @param cursor: last returned result; default=(last_item_created_at, id)
        @param limit: max number of records to return
        @param sort: a list of tuples (column, sort_direction); default=[('created_at', 'asc'), ('id', 'asc')]
        @param filters: filtering criteria: {'column_name': column_value}
        @param dynamic_filters: list of tuples: (column, operator, value),
            example: ('created_at', '>', datetime.utcnow())
        @return: list of items matching criteria, starting from the given cursor
        """
        assert limit and limit > 0
        sort = sort if isinstance(sort, list) and len(sort) else [('created_at', 'asc'), ('id', 'asc')]

        q = select(self.model)
        ordering = [
            getattr(self.model, col).asc() if direction.lower() == 'asc' else getattr(self.model, col).desc()
            for col, direction in sort
        ]
        q = q.order_by(*ordering)
        if filters:
            q = q.filter_by(**filters)
        if dynamic_filters:
            dynamic_conditions = [
                getattr(getattr(self.model, column), operator)(value)  # creates sqlalchemy expression object
                for column, operator, value in dynamic_filters
            ]
            q = q.filter(and_(*dynamic_conditions))
        if cursor:
            cursor_datetime, cursor_id = cursor
            cursor_conditions = [
                (getattr(self.model, 'created_at') > cursor_datetime) |  # logical OR
                ((getattr(self.model, 'created_at') == cursor_datetime) & (getattr(self.model, 'id') > cursor_id))
            ]
            q = q.filter(and_(*cursor_conditions))
        q = q.limit(limit)
        return list((await self.session.execute(q)).scalars().all())
