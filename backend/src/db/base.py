import os

from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv(find_dotenv('.env.dev'))  # TODO replace hard coded values with configuration class
db_path = f'postgresql+asyncpg://' + f'{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5432/postgres'
# TODO consider using `alchemical` to set up db

engine = create_async_engine(db_path)
Session = async_sessionmaker(engine, expire_on_commit=False)



