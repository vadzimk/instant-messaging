from pydantic import BaseModel, EmailStr


class UserCreateOut(BaseModel):
    email: EmailStr


class UserCreateIn(UserCreateOut):
    password: str


class UserLoginIn(BaseModel):
    email: EmailStr
    password: str


class UserLoginOut(BaseModel):
    access_token: str
    token_type: str
