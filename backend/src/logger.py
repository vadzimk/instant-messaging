import logging
import sys

from loguru import logger

from src.settings import server_settings

LOG_LEVEL = server_settings.LOG_LEVEL

logger.remove()

# Add console logging
logger.add(
    sys.stdout,
    level=server_settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Add file logging with daily rotation
logger.add(
    "logs/app.log",
    rotation=server_settings.LOG_ROTATION,
    level=logging.DEBUG,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


# https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # get corresponding Loguru level if exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # find caller from where originated log message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        message = record.getMessage()
        extra_data = record.__dict__.get('extra', {})

        if extra_data:
            logger.opt(depth=depth, exception=record.exc_info).log(level, f"{message} - {extra_data}")
        else:
            logger.opt(depth=depth, exception=record.exc_info).log(level, message)


# The trick here is to call the basicConfig method from the standard logging module
# to set our custom interception handler. This way, every log call made with the root logger,
# even ones from external libraries, will go through it and be handled by Loguru.
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# if the above is not sufficient
# as in uvicorn, which defines two main loggers: uvicorn.error and uvicorn.access.
# By retrieving those loggers and changing their handler, we force them to go through Loguru as well.
for uvicorn_logger_name in ['uvicorn.error', 'uvicorn.access']:
    uvicorn_logger = logging.getLogger(uvicorn_logger_name)
    uvicorn_logger.propagate = False
    uvicorn_logger.handlers = [InterceptHandler()]

__all__ = ['logger']  # make these variables available when importing this module
