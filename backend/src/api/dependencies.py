import logging
from typing import Annotated

from src.services.auth import decode_and_validate_token
from src.services.contact_service import ContactService
from src.services.message_service import MessageService
from src.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.db import models as m
from src.db.session import Session  # local import to avoid circular import
from src.services.user_service import UserService
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import (ExpiredSignatureError, ImmatureSignatureError, InvalidAlgorithmError, InvalidAudienceError,
                 InvalidKeyError, InvalidSignatureError, InvalidTokenError, MissingRequiredClaimError)
from src.exceptions import CouldNotValidateCredentials

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login')

logger = logging.getLogger(__name__)


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    if token is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    try:
        token_payload = decode_and_validate_token(token)
        user_email = token_payload['sub']
    except (
            ExpiredSignatureError,
            ImmatureSignatureError,
            InvalidAlgorithmError,
            InvalidAudienceError,
            InvalidKeyError,
            InvalidSignatureError,
            InvalidTokenError,
            MissingRequiredClaimError,
    ) as error:
        raise CouldNotValidateCredentials(str(error))
    if user_email is None:
        raise CouldNotValidateCredentials("user_email is None")
    return user_email


async def get_uow():
    async with Session() as session:
        async with SqlAlchemyUnitOfWork(session) as uow:
            yield uow


async def get_user_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return UserService(uow)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_contact_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return ContactService(uow)


ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]


async def get_message_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return MessageService(uow)


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]


async def authenticated_user(
        user_email: Annotated[str, Depends(get_current_user_id)],
        user_service: UserService = Depends(get_user_service)
) -> m.User:
    user = await user_service.get_existing_user({'email': user_email})
    if user is None:
        raise CouldNotValidateCredentials()
    return user
