from fastapi import HTTPException
from starlette import status


class EntityNotFoundError(Exception):
    pass


class CouldNotValidateCredentials(HTTPException):
    def __init__(self, message="Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )
