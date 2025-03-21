import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.orm import aliased
from starlette import status

from src.db.session import Session
from src.main import app
from src.db import models as m
from .conftest import decode_access_token
from src import schemas as p
from ..data.data import user1, user2



def test_signup_user(signup_user1_response):
    print(signup_user1_response.json())
    assert signup_user1_response.status_code == status.HTTP_201_CREATED, \
        f"Expected status code {status.HTTP_201_CREATED}, got {signup_user1_response.status_code}"
    assert signup_user1_response.json().get("email") == user1.email, \
        f"Expected email {user1.email}, got {signup_user1_response.json().get('email')}"



async def test_login_user_using_authorization_header(login_user1_response):
    data = login_user1_response.json()
    print(data)
    assert data.get('token_type') == 'bearer', "json body bearer not set"
    access_token = data.get('access_token')
    validated_result_payload = decode_access_token(access_token)
    print("validated_result_payload")
    print(validated_result_payload)
    assert validated_result_payload.get('sub') == user1.email, "token subject not set to email"


async def test_authenticated_request_rejects_if_not_authenticated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        auth_header = f'Bearer xxx.xxx.xxx'
        res = await client.post('/api/me', headers={'Authorization': auth_header})
    print(res.status_code)
    print(res.json())
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, "Unauthenticated request accepted on protected path, but should be rejected"



async def test_authenticated_request_accepts_valid_header(client_with_auth_user1):
    res = await client_with_auth_user1.post('/api/me')
    print(res.status_code)
    print(res.json())
    assert res.status_code == status.HTTP_200_OK, \
        "Authenticated request is rejected on protected path but should be accepted"



async def test_create_contact(login_user1_response, signup_user2_response, create_u2_contact_for_u1_response):
    print("create_contact_response.status_code", create_u2_contact_for_u1_response.status_code)
    print(create_u2_contact_for_u1_response.json())

    # check contact in database
    async with Session() as session:
        async with session.begin():
            u1 = await session.scalar(
                select(m.User).where(m.User.email == login_user1_response.json().get('email')))
            u2 = await session.scalar(
                select(m.User).where(m.User.id == signup_user2_response.json().get('id')))
            assert create_u2_contact_for_u1_response.json().get(
                'id') == str(u2.id), "Created contact id does not match with created user id"
            UserContact = aliased(m.User)
            q = (select(m.User, UserContact)
                 .join(m.Contact.user)
                 .join(UserContact, m.Contact.contact_user)
                 .where(m.User.id == u1.id))
            res = (await session.execute(q)).all()
            found = False
            for row in res:
                user, contact = row
                if contact.email == user2.email:
                    found = True
            assert found, f"Could not find {user2.email} in among contacts of user {login_user1_response.json().get('email')}"



async def test_get_contacts(client_with_auth_user1, create_u2_contact_for_u1_response):
    res = await client_with_auth_user1.get('/api/contacts')
    print(res.json())
    assert create_u2_contact_for_u1_response.json() in res.json().get(
        'contacts'), "Created contact not found in get_contacts response"



async def test_get_messages(client_with_auth_user1, send_message_u1_u2):
    async with Session() as session:
        q = select(m.User).where(m.User.email == user2.email)
        u2 = await session.scalar(q)
        print(u2.id)

    res = await client_with_auth_user1.get(
        f'/api/chats/{u2.id}'
    )
    valid_response = p.GetMessagesSchema.model_validate(res.json())
    valid_msg = p.GetMessageSchema.model_validate(valid_response.messages[0])
    _, expected_content = send_message_u1_u2
    assert valid_msg.content == expected_content, "Message content does not equal to expected"
    assert str(valid_msg.user_to_id) == str(u2.id), "user_to_id does not equal to expected"
