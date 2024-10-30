from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar, Generic, Dict, Any, List, Optional, Tuple
from uuid import UUID

T = TypeVar('T')


class AbstractRepository(Generic[T]):
    @abstractmethod
    async def add(self, entity: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    async def get(self, filters: Dict[str, Any]) -> Optional[T]:
        """
        Retrieves first result or None
        @param filters: dictionary with key as entity attribute and value as equality condition
        @return: first result
        """
        raise NotImplementedError()

    @abstractmethod
    async def update(self, filters: Dict[str, Any], update: Dict[str, Any]) -> Optional[T]:
        raise NotImplementedError()

    async def delete(self, filters: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list(
            self,
            cursor: Optional[Tuple[datetime, str | UUID]],
            limit: Optional[int],
            sort: Optional[List[Tuple[str]]] = None,
            filers: Optional[Dict[str, Any]] = None,
            *,
            dynamic_filters: Optional[List[Tuple[str, str, Any]]] = None
    ) -> List[T]:
        """
        Retrieves a paginated, filtered, and sorted list of items starting from a cursor position.
        @param cursor: a tuple: (last_item_timestamp, id)
        @param limit: max number of records to return
        @param sort: a list of tuples where
        @param filers: filtering criteria
        @param dynamic_filters: list of tuples: (column, operator, value),
            example: ('created_at', '>', datetime.utcnow())
        @return: list of items matching criteria, starting from the given cursor
        """
        raise NotImplementedError()
