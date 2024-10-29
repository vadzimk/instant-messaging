from dataclasses import field
from datetime import datetime
from typing import Optional, List, Any, Tuple
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel, EmailStr


class BaseModel(PydanticBaseModel):
    model_config = {
        "from_attributes": True,  # model_validate will be able to take a dict or orm.model
    }


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


class CreateContactSchema(BaseModel):
    email: str


class GetContactSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str


class GetContactsSchema(BaseModel):
    contacts: List[GetContactSchema]


class CreateMessageSchema(BaseModel):
    contact_id: UUID
    content: str


class GetMessageSchema(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    user_from_id: UUID
    user_to_id: UUID


class GetMessagesSchema(BaseModel):
    messages: List[GetMessageSchema]


class ValidationError(BaseModel):
    type: str  # related type
    loc: Tuple[str]  # location of error
    msg: str
    input: Any  # actual input
    url: str  # more info about this error


class SioResponseSchema(BaseModel):
    success: bool = True
    data: Any
    errors: List[ValidationError] = field(default_factory=list)

    model_config = {
        'arbitrary_types_allowed': True
    }
