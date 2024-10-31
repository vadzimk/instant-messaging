from datetime import datetime
from typing import List
from uuid import UUID

from .base_schema import BaseModel


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
