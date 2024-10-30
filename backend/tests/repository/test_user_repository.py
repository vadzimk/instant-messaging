from pprint import pprint
from typing import AsyncGenerator, List

import pytest
from sqlalchemy import select

from src.repository.user_repository import UserRepository
from src import models as m
from tests.data.data import user1


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


# @pytest.mark.only
async def test_delete_user(insert_user1, async_session):
    expected_user_id = insert_user1.id
    user_repository = UserRepository(async_session)
    await user_repository.delete({'id': insert_user1.id})
    q = select(m.User).where(m.User.id == expected_user_id)
    res = await async_session.scalar(q)
    assert res is None, f"User delete failed. Expected returned user to be None, but got {res}"


class TestRepositoryList:
    number_of_users_to_create = 30

    @pytest.mark.parametrize('insert_users', [number_of_users_to_create], indirect=True)
    async def test_when_no_args_returns_first_ten_records(self, insert_users: List[m.User], async_session):
        assert len(insert_users) == self.number_of_users_to_create, "number of created users does is not as expected"
        user_repository = UserRepository(async_session)
        expected_length = 10
        res = await user_repository.list()
        assert len(res) == expected_length, "length of result ont as expected"

    @pytest.mark.parametrize('insert_users', [number_of_users_to_create], indirect=True)
    async def test_when_limit_returns_first_limit_records(self, insert_users: List[m.User], async_session):
        user_repository = UserRepository(async_session)
        expected_len = 4
        res = await user_repository.list(limit=expected_len)
        assert len(res) == expected_len, "length of result ont as expected"

    @pytest.mark.parametrize('insert_users', [number_of_users_to_create], indirect=True)
    async def test_when_filter_respects(self, insert_users: List[m.User], async_session):
        user_repository = UserRepository(async_session)
        res = await user_repository.list(filters={'last_name': 'odd'})
        assert all(u.last_name == 'u-test-repository-odd' for u in res), "filter not respected"

    @pytest.mark.parametrize('insert_users', [number_of_users_to_create], indirect=True)
    async def test_when_dynamic_filter_respects(self, insert_users: List[m.User], async_session):
        user_repository = UserRepository(async_session)
        res = await user_repository.list(dynamic_filters=[('first_name', 'like', 'u-test-repository-%0')])
        assert len(res) == self.number_of_users_to_create / 10

    @pytest.mark.parametrize('insert_users', [number_of_users_to_create], indirect=True)
    async def test_when_cursor_respects(self, insert_users: List[m.User], async_session):
        user_repository = UserRepository(async_session)
        res1 = await user_repository.list(
            dynamic_filters=[('first_name', 'like', 'u-test-repository-%')],
            limit=3
        )
        last_item: m.User = res1[-1]

        res2 = await user_repository.list(
            cursor=(last_item.created_at, last_item.id),
            dynamic_filters=[('first_name', 'like', 'u-test-repository-%')],
            limit=3
        )
        assert int(res2[0].first_name.replace("u-test-repository-", "")) == int(
            last_item.first_name.replace("u-test-repository-",
                                         "")) + 1, (f"Expected the first item in the second result set "
                                                    f"to be the next user after '{last_item.first_name}', "
                                                    f"but got '{res2[0].first_name}' instead. "
                                                    f"This indicates that the cursor pagination may not be functioning")

    @pytest.mark.parametrize('insert_users', [number_of_users_to_create], indirect=True)
    async def test_when_sort_respects(self, insert_users: List[m.User], async_session):
        user_repository = UserRepository(async_session)
        res = await user_repository.list(
            dynamic_filters=[('first_name', 'like', 'u-test-repository-%')],
            sort=[('first_name', 'desc')]
        )
        fnames = [u.first_name for u in res]
        expected_fnames = sorted(fnames, reverse=True)
        assert fnames == expected_fnames, f"Sorting order not as expected"
