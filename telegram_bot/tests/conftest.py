import dataclasses
import os
from typing import AsyncGenerator, Dict, Optional
import pytest_asyncio
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import MetaData, insert, delete, Row
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine, AsyncConnection

load_dotenv(find_dotenv('.env.dev'))

user1 = {
    "email": "u1@mail.com",
    "first_name": "u1",
    "last_name": "",
    "hashed_password": "secret",
    "is_active": True
}


@dataclasses.dataclass
class Tables:
    User: any
    Contact: any
    Message: any


@pytest_asyncio.fixture(loop_scope='session', scope='session')  # loop_scope > cache_scope
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    db_path = f'postgresql+asyncpg://' \
              f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    print("db_path", db_path)
    engine = create_async_engine(db_path)
    yield engine


@pytest_asyncio.fixture(loop_scope='session', scope='session')
async def load_tables(db_engine: AsyncEngine) -> Tables:
    # reflect existing database structure for convenience
    metadata = MetaData()
    async with db_engine.begin() as conn:
        await conn.run_sync(metadata.reflect)

    return Tables(
        User=metadata.tables['users'],
        Contact=metadata.tables['contacts'],
        Message=metadata.tables['contacts']
    )


@pytest_asyncio.fixture(loop_scope='session', scope='session')
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    Session = async_sessionmaker(db_engine)
    async with Session() as session:
        yield session


@pytest_asyncio.fixture(loop_scope='session', scope='session')
async def create_user1(db_session, load_tables) -> AsyncGenerator[Optional[Dict[str, str]], None]:
    stmt = insert(load_tables.User).values(**user1).returning(load_tables.User)
    res = await db_session.execute(stmt)
    await db_session.commit()
    inserted_user = res.fetchone()
    inserted_user_dict = None
    if inserted_user:
        column_names = res.keys()
        inserted_user_dict = dict(zip(column_names, inserted_user))
    yield inserted_user_dict
    stmt = delete(load_tables.User).where(load_tables.User.c.email == user1.get('email'))
    await db_session.execute(stmt)
    await db_session.commit()
