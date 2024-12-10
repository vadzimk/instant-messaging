import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv, find_dotenv


@pytest.fixture(scope='session', autouse=True)
def load_env():
    if os.getenv('ENV') != 'development':
        # variables were exported in container
        print("ENV=development not set. Will expect environment variables set in the shell")
        pass
    else:
        env_filename = '.env.dev'
        print(f"Loading environment variables from file {env_filename}")
        load_dotenv(find_dotenv(env_filename))

