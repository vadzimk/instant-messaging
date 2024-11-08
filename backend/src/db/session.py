from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.main import server_settings

db_path = f'postgresql+asyncpg://' \
          f'{server_settings.POSTGRES_USER}:{server_settings.POSTGRES_PASSWORD}@{server_settings.POSTGRES_HOST}:{server_settings.POSTGRES_PORT}/{server_settings.POSTGRES_DB}'

# TODO consider using `alchemical` to set up db

engine = create_async_engine(db_path)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()
