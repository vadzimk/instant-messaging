from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from starlette import status

from src.api.sio import redis_manager
from src.db.session import engine
from src.schemas import GetHealthSchema

router = APIRouter()
from src.logger import logger


@router.get('', response_model=GetHealthSchema, status_code=status.HTTP_200_OK)
async def health_check():
    postgres = {"connected": False, "error": None}
    redis = {"connected": False, "error": None}

    # check postgres connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
            postgres['connected'] = True
    except Exception as err:
        postgres['error'] = str(err)

    # check postgres connectivity
    try:
        await redis_manager.redis.ping()
        redis['connected'] = True
    except Exception as err:
        redis['error'] = str(err)

    is_healthy = postgres.get('connected') and redis.get('connected')

    content = {
        'is_healthy': is_healthy,
        'postgres': postgres,
        'redis': redis,
    }
    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=content
        )
    return content
