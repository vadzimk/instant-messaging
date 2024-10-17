from fastapi import FastAPI

from .api.api import router

app = FastAPI(debug=True, openapi_url='/openapi/app.json', docs_url='/docs/app')
app.include_router(router)