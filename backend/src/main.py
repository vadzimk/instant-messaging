import logging
import socketio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .api.sio import sio
from .utils import setup_logging
from .api.api import router

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
