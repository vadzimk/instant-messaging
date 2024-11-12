from .base_schema import BaseModel


class SubscribeToNotifications(BaseModel):
    user_email: str
    tg_user_id: int
