from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreateOut(BaseModel):
    email: EmailStr
    first_name: str
    last_name: Optional[str]


class UserCreateIn(UserCreateOut):
    password: str


class User(UserCreateOut):
    id: int
    is_active: bool


class UserLoginOut(UserCreateOut):
    access_token: str
    token_type: str


class AddNewContactIn(BaseModel):
    email: str


class AddNewContactOut(AddNewContactIn):
    email: str
    first_name: str
    last_name: str
