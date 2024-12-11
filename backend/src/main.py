import logging
import socketio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api.sio import sio
from src.api.api import router as api_router
from src.api.telegram import router as telegram_router
from src.api.health import router as health_router

from src.middleware.catch_exceptions import CatchExceptionsMiddleware
from src.settings import server_settings
from src.utils import setup_logging

setup_logging(server_settings.LOG_LEVEL)

logger = logging.getLogger(__name__)
app = FastAPI(debug=True, openapi_url='/openapi.json', docs_url='/docs')

# == first middleware is executed first on responses ==
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],  # allow all origins
                   allow_credentials=True,  # support cookies for cross-origin requests
                   allow_methods=["*"],  # allow all http methods
                   allow_headers=["*"], )  # allow all headers
app.add_middleware(CatchExceptionsMiddleware)
# == last middleware is executed first on requests ==


app.include_router(api_router, prefix='/api')
app.include_router(telegram_router, prefix='/service/telegram')  # handles telegram bot service-to-service requests
app.include_router(health_router, prefix='/health')
app.mount('/socket.io/', socketio.ASGIApp(sio))  # socketio adds automatically /socket.io/ to the URL.
