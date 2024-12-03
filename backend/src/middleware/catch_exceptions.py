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

from src.settings import server_settings

logger = logging.getLogger(__name__)


async def custom_exception_handler(request: Request, exc: Exception):
    logger.error(f"{type(exc).__name__} {exc}")
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Default status code
    detail = str(exc)  # Default detail message
    headers = {}

    if isinstance(exc, e.IntegrityErrorException):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, e.UserNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
        detail = "User not found"

    elif isinstance(exc, e.AlreadyRegisteredException):
        status_code = status.HTTP_400_BAD_REQUEST
        detail = "User already registered"

    elif isinstance(exc, e.IncorrectCredentialsException):
        status_code = status.HTTP_400_BAD_REQUEST
        detail = "Incorrect credentials"

    elif isinstance(exc, e.CouldNotValidateCredentials):
        status_code = status.HTTP_401_UNAUTHORIZED
        headers = {"WWW-Authenticate": "Bearer"}
        detail = "Could not validate credentials"

    else:
        if server_settings.ENV == 'production':
            detail = "Unhandled exception occurred"
        else:  # not in production
            # error detail in response will contain exception detail
            logger.error(
                "Unhandled exception occurred",
                exc_info=(server_settings.LOG_LEVEL == logging.DEBUG)  # includes Stack Trace
            )

    return JSONResponse(status_code=status_code, content={'detail': detail}, headers=headers)


class CatchExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            return await custom_exception_handler(request, exc)
