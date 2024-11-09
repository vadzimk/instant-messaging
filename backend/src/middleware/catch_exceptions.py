# cannot catch Exception globally in starlette using @app.exception_handler
# https://github.com/fastapi/fastapi/issues/2750#issuecomment-772976371
# use this custom middleware instead

import logging
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from src import exceptions as e

from starlette.responses import Response

logger = logging.getLogger(__name__)


async def custom_exception_handler(request: Request, exc: Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Default status code
    detail = str(exc)  # Default detail message
    headers = {}

    if isinstance(exc, e.IntegrityErrorException):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, e.UserNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, e.AlreadyRegisteredException):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, e.IncorrectCredentialsException):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, e.CouldNotValidateCredentials):
        status_code = status.HTTP_401_UNAUTHORIZED
        headers = {"WWW-Authenticate": "Bearer"}
        detail = "Could not validate credentials"

    return JSONResponse(status_code=status_code, content={'detail': detail}, headers=headers)


class CatchExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            return await custom_exception_handler(request, exc)
