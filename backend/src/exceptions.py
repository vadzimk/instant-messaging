from fastapi import HTTPException
from starlette import status


class CouldNotValidateCredentials(HTTPException):
    def __init__(self, message="Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class EntityNotFoundError(Exception):
    pass


class IntegrityErrorException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class AlreadyRegisteredException(Exception):
    pass


class IncorrectCredentialsException(Exception):
    pass
