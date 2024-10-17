from pydantic import BaseModel, EmailStr


class UserCreateOut(BaseModel):
    email: EmailStr


class UserCreateIn(UserCreateOut):
    password: str

