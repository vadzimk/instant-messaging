import logging
import sys

from loguru import logger

from src.settings import server_settings

LOG_LEVEL = server_settings.LOG_LEVEL

logger.remove()
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
           " - {extra}",
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

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# The trick here is to call the basicConfig method from the standard logging module
# to set our custom interception handler. This way, every log call made with the root logger,
# even ones from external libraries, will go through it and be handled by Loguru.
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# if the above is not sufficient
# as in uvicorn, which defines two main loggers: uvicorn.error and uvicorn.access.
# By retrieving those loggers and changing their handler, we force them to go through Loguru as well.
for logger_name in ['aiohttp.server', 'aiohttp.access', 'aiohttp.client', 'kafka']:
    dependency_logger = logging.getLogger(logger_name)
    dependency_logger.propagate = False
    dependency_logger.handlers = [InterceptHandler()]

__all__ = ['logger'] # make these variables available when importing this module
