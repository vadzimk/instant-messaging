from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr


class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True
    }


class GetUserSchema(BaseSchema):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: Optional[str]


class CreateUserSchema(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: Optional[str]
    password: str


class LoginUserSchema(GetUserSchema):
    access_token: str
    token_type: str


class CreateContactSchema(BaseSchema):
    email: str


class GetContactSchema(CreateContactSchema):
    first_name: str
    last_name: str


class GetContactsSchema(BaseSchema):
    contacts: List[GetContactSchema]
