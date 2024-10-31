from typing import Optional
from uuid import UUID

from pydantic import EmailStr

from .base_schema import BaseModel


class GetUserSchema(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: Optional[str]


class CreateUserSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: Optional[str]
    password: str


class LoginUserSchema(GetUserSchema):
    access_token: str
    token_type: str
