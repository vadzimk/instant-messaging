from typing import Optional

from pydantic import BaseModel, EmailStr


class UserSignupOut(BaseModel):
    email: EmailStr
    first_name: str
    last_name: Optional[str]


class UserSignupIn(UserSignupOut):
    password: str


class User(UserSignupOut):
    id: int
    is_active: bool


class UserLoginOut(UserSignupOut):
    access_token: str
    token_type: str


class AddContactIn(BaseModel):
    email: str


class AddContactOut(AddContactIn):
    email: str
    first_name: str
    last_name: str
