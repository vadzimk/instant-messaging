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
        raise NotImplementedError()

    @abstractmethod
    async def update(self, filters: Dict[str, Any], update: Dict[str, Any]) -> Optional[T]:
        raise NotImplementedError()

    @abstractmethod
    async def list(
            self,
            cursor: Optional[Tuple[datetime, str | UUID]],
            limit: Optional[int],
            sort: Optional[str] = 'created_at',
            filers: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """
        Retrieves a paginated, filtered, and sorted list of items starting from a cursor position.
        @param cursor: a tuple of the last item timestamp and id
        @param limit: max number of records to return
        @param sort: sort field, typically a timestamp
        @param filers: filtering criteria
        @return: list of items matching criteria, starting from the given cursor
        """
        raise NotImplementedError()
