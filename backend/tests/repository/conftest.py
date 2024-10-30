import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Session


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()
