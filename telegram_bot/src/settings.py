import os

from aiogram import Bot
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False,
        extra='ignore'
    )

    TELEGRAM_BOT_TOKEN: str
    WEB_APP_PORT: int  # aiohttp port


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


server_settings = configure_server_settings()

bot = Bot(token=server_settings.TELEGRAM_BOT_TOKEN)
