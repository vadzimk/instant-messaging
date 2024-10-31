from typing import List
from uuid import UUID

from .base_schema import BaseModel


class CreateContactSchema(BaseModel):
    email: str


class GetContactSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str


class GetContactsSchema(BaseModel):
    contacts: List[GetContactSchema]
