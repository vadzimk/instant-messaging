from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .services.auth import AuthorizeRequestMiddleware
from .api.api import router

app = FastAPI(debug=True, openapi_url='/openapi/app.json', docs_url='/docs/app')

app.add_middleware(AuthorizeRequestMiddleware)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],  # allow all origins
                   allow_credentials=True,  # support cookies for cross-origin requests
                   allow_methods=["*"],  # allow all http methods
                   allow_headers=["*"],)  # allow all headers
# last middleware is executed first on requests


app.include_router(router)
