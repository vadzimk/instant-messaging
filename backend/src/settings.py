import logging
import os
from typing import Optional

from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False,
        extra='ignore'
    )

    POSTGRES_APP_USER: str = 'postgres'
    POSTGRES_APP_PASSWORD: str = 'postgres'
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = 'postgres'

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    AUTH_ON: bool = True
    BOT_BASE_URL: str = 'http://localhost:8003'

    JWT_ISSUER: str = 'example.com'
    JWT_AUDIENCE: str = '127.0.0.1:8000'
    JWT_SCOPE: str = 'openid'
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_PUBLIC_KEY: Optional[str] = None
    LOG_LEVEL: int = logging.INFO


def configure_server_settings():
    """ Configures Server settings
    Must be called before all local imports in main.py,
     so that dependencies get the environment variables populated
    """
    if os.getenv('ENV') != 'development':
        # variables were exported in container
        pass
    else:
        load_dotenv(find_dotenv('.env.dev'))

    return ServerSettings()

server_settings = configure_server_settings()