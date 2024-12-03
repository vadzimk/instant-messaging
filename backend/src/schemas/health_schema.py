from typing import Optional

from .base_schema import BaseModel


class DbStatus(BaseModel):
    connected: bool
    error: Optional[str]


class GetHealthSchema(BaseModel):
    is_healthy: bool
    postgres: DbStatus
    redis: DbStatus
