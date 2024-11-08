import os

from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False,
        extra='ignore'
    )

    TELEGRAM_BOT_TOKEN: str


def configure_server_settings():
    """ Configures Server settings
    Must be called before all local imports,
     so that dependencies get the environment variables populated
    """
    if os.getenv('ENV') != 'development':
        # variables were exported in container
        pass
    else:
        load_dotenv(find_dotenv('.env.dev'))
    return ServerSettings()
