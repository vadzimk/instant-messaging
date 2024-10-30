import pytest
from sqlalchemy import select

from src.repository.user_repository import UserRepository
from src import models as m
from tests.data.data import user1


@pytest.fixture
async def insert_user1(async_session):
    user_repository = UserRepository(async_session)
    user_fields = {k: v for k, v in user1.model_dump().items() if k != 'password'}
    user_fields['hashed_password'] = user1.password
    user = m.User(**user_fields)
    print(user)
    await user_repository.add(user)
    yield user
    await async_session.delete(user)
    await async_session.commit()


async def test_add_user(insert_user1, async_session):
    q = select(m.User).where(m.User.email == user1.email)
    res = await async_session.scalar(q)
    assert res.email == user1.email, "inserted user's email did not match with data of user1"


async def test_get_user(insert_user1, async_session):
    user_repository = UserRepository(async_session)
    user_from_repository = await user_repository.get({'email': user1.email})
    assert isinstance(user_from_repository, m.User), "user form repository must be database model instance"
    assert user_from_repository.email == user1.email, "user from repository email did not match with data of user1"


async def test_update_user(insert_user1, async_session):
    user_repository = UserRepository(async_session)
    expected_last_name = 'Bobbis'
    updated_user = await user_repository.update({'email': user1.email}, {'last_name': expected_last_name})
    assert updated_user.last_name == expected_last_name, "returned updated user's last_name is not as expected"
    q = select(m.User).where(m.User.email == user1.email)
    user_from_db = await async_session.scalar(q)
    assert user_from_db.last_name == expected_last_name, "user_from_db after update is not as expected"




