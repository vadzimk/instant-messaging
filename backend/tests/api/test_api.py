from pathlib import Path

import jwt
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.orm import aliased

from starlette import status
from cryptography.x509 import load_pem_x509_certificate
from src.main import app
from src.api.schemas import AddNewContactIn
from src.db import Session
from src import models as m


def test_signup_user(signup_user1_response, user1):
    print(signup_user1_response)
    assert signup_user1_response.status_code == status.HTTP_201_CREATED, \
        f"Expected status code {status.HTTP_201_CREATED}, got {signup_user1_response.status_code}"
    assert signup_user1_response.json().get("email") == user1.email, \
        f"Expected email {user1.email}, got {signup_user1_response.json().get('email')}"


def decode_access_token(access_token):
    # validate token on the client for each request
    private_key_path = Path(__file__).parent.parent.parent / 'jwt_keys/public_key.pem'
    public_key_text = private_key_path.read_text()
    public_key = load_pem_x509_certificate(public_key_text.encode('utf-8')).public_key()
    validated_result_payload = jwt.decode(access_token, key=public_key, algorithms=['RS256'],
                                          audience=["http://127.0.0.1:8000/"])
    return validated_result_payload


async def test_login_user_using_authorization_header(login_user1_response, user1):
    data = login_user1_response.json()
    print(data)
    assert data.get('token_type') == 'bearer', "json body bearer not set"
    access_token = data.get('access_token')
    validated_result_payload = decode_access_token(access_token)
    print("validated_result_payload")
    print(validated_result_payload)
    assert validated_result_payload.get('sub') == user1.email, "token subject not set to email"


@pytest.fixture(scope="function")
async def authenticate_user1_with_header_response(login_user1_response):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        auth_header = f'Bearer {login_user1_response.json().get("access_token")}'
        res = await client.post('/api/me', headers={'Authorization': auth_header})
        yield res


async def test_authenticated_request_rejects_if_not_authenticated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        auth_header = f'Bearer xxx.xxx.xxx'
        res = await client.post('/api/me', headers={'Authorization': auth_header})
    print(res.status_code)
    print(res.json())
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, "unauthenticated request is not rejected on protected path"


async def test_authenticated_request_accepts_valid_header(authenticate_user1_with_header_response):
    print(authenticate_user1_with_header_response.status_code)
    print(authenticate_user1_with_header_response.json())
    assert authenticate_user1_with_header_response.status_code == status.HTTP_200_OK, \
        "authenticated request is rejected on protected path"


@pytest.mark.only
async def test_add_contact(login_user1_response, signup_user2_response):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        auth_header = f'Bearer {login_user1_response.json().get("access_token")}'
        new_contact = AddNewContactIn(**signup_user2_response.json())
        res = await client.post(
            '/api/add-contact',
            headers={'Authorization': auth_header},
            json=new_contact.model_dump()
        )
        print(res.status_code)
        print(res.json())
        assert res.json().get('email') == new_contact.email, "Created contact email does not match"

        # check contact in database
        async with Session() as session:
            async with session.begin():
                u1 = await session.scalar(
                    select(m.User).where(m.User.email == login_user1_response.json().get('email')))
                u2 = await session.scalar(
                    select(m.User).where(m.User.first_name == signup_user2_response.json().get('email')))
                UserContact = aliased(m.User)
                q = (select(m.User, UserContact)
                     .join(m.Contact, m.User.id == m.Contact.c.user_id)
                     .join(UserContact, m.Contact.c.contact_id == UserContact.id)
                     .where(m.User.id == u1.id))
                res = (await session.execute(q)).all()
                found = False
                for row in res:
                    user, contact = row
                    if contact.email == new_contact.email:
                        found=True
                assert found, f"Could not find {new_contact.email} in database"
