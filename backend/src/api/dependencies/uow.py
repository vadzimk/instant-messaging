from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Session
from src.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork


async def get_db():
    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()


async def get_uow():
    async with Session() as session:
        async with SqlAlchemyUnitOfWork(session) as uow:
            yield uow
