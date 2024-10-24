from typing import Optional, List

from pydantic import BaseModel, EmailStr


class GetUserSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: Optional[str]


class CreateUserSchema(GetUserSchema):
    password: str


class LoginUserSchema(GetUserSchema):
    access_token: str
    token_type: str


class CreateContactSchema(BaseModel):
    email: str


class GetContactSchema(CreateContactSchema):
    email: str
    first_name: str
    last_name: str


class GetContactsSchema(BaseModel):
    contacts: List[GetContactSchema]
