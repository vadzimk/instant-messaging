from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.abstract_repository import AbstractRepository
from ..db import models as m


class UserRepository(AbstractRepository[m.User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, m.User)
