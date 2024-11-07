import os

import pytest
from dotenv import load_dotenv, find_dotenv


@pytest.fixture(scope='session', autouse=True)
def load_env():
    if os.getenv('ENV') != 'development':
        # variables were exported in container
        print("ENV=development not set. Will expect environment variables set in the shell")
        pass
    else:
        print("Loading environment variables")
        load_dotenv(find_dotenv('.env.dev'))

