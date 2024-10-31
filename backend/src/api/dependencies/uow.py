from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Session
from src.services.user_service import UserService
from src.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork





async def get_uow():
    async with Session() as session:
        async with SqlAlchemyUnitOfWork(session) as uow:
            yield uow


async def get_user_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return UserService(uow)
