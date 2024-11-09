import logging

from fastapi import APIRouter
from starlette import status
from src import exceptions as e
from src import schemas as p
from src.api.dependencies import UserServiceDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/subscriptions', status_code=status.HTTP_204_NO_CONTENT)
async def subscribe_to_notifications(
        user_data: p.SubscribeToNotifications,
        user_service: UserServiceDep
):
    logger.info(f'subscribe user {user_data}')
    await user_service.subscribe_notifications(user_data)


# @router.get('/test-user-not-found')
# async def test_user_not_found():
#     raise e.UserNotFoundException("Test user not found")
