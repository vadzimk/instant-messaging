import logging
import sys


def setup_logging(loglevel):
    FORMAT = "%(asctime)s | %(levelname)s | [%(name)s] | (%(filename)s:%(lineno)d) | %(message)s"
    formatter = logging.Formatter(FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(loglevel)

