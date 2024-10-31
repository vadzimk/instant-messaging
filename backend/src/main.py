import logging
import socketio
from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.api.sio import sio
from src import exceptions as e
from src.utils import setup_logging
from src.api.api import router

setup_logging(logging.INFO)

logger = logging.getLogger(__name__)
app = FastAPI(debug=True, openapi_url='/openapi.json', docs_url='/docs')

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],  # allow all origins
                   allow_credentials=True,  # support cookies for cross-origin requests
                   allow_methods=["*"],  # allow all http methods
                   allow_headers=["*"], )  # allow all headers
# last middleware is executed first on requests


app.include_router(router, prefix='/api')
app.mount('/socket.io/', socketio.ASGIApp(sio))  # socketio adds automatically /socket.io/ to the URL.


async def custom_exception_handler(request: Request, exc: Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Default status code
    detail = str(exc)  # Default detail message

    if isinstance(exc, e.IntegrityErrorException):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, e.UserNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, e.AlreadyRegisteredException):
        status_code = status.HTTP_400_BAD_REQUEST

    elif isinstance(exc, e.IncorrectCredentialsException):
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(status_code=status_code, content={'detail': detail})


@app.exception_handler(Exception)  # Catch all exceptions
async def handle_exception(request: Request, exc: Exception):
    return await custom_exception_handler(request, exc)
