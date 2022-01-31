# Python default modules
import json
import pendulum
import sys, logging
from pprint import pformat
from types import FrameType
from typing import cast

# Python modules installed using pipenv
from loguru import logger
from loguru._defaults import LOGURU_FORMAT  # noqa: WPS436
from das_sankhya.middlewares.asgi_correlation_id import CorrelationIdMiddleware
from das_sankhya.middlewares.asgi_correlation_id.context import correlation_id
from starlette_context import context

# App core modules
from das_sankhya.config.application import settings

# Lib modules
from das_sankhya.utils.json import DateTimeEncoder

# Constants
LOGGING_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO
LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.asgi", "uvicorn.access", "gunicorn", "gunicorn.error", "gunicorn.access")

def set_log_extras(record):
    record["extra"]["datetime"] = pendulum.now("UTC")
    record["extra"]["app_name"] = settings.PROJECT_NAME
    record["extra"]["correlation_id"] = correlation_id.get()
    if context.exists():
        record["extra"]["request_id"] = correlation_id.get()
    else:
        record["extra"]["request_id"] = None

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(),
        )


def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body dur<green>{extra[correlation_id]}</green> | 
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    # format_string = LOGURU_FORMAT
    # format_string = '<green>{extra[datetime]}</green> | <green>{extra[app_name]}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | <level>{extra}</level>'
    format_string = 'XXXXX <green>{extra[request_id]}</green> | <green>{extra[correlation_id]}</green> | <green>{extra[datetime]}</green> | <green>{extra[app_name]}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    # format_string = "[{time}] [{extra[application_name]}] [{extra[correlationId]}] [{level}] - {name}:{function}:{line} - {message}"

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    logger.debug(format_string)
    return format_string

# logging configuration
logging.getLogger().handlers = [InterceptHandler()]
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name).handlers = [InterceptHandler(level=LOGGING_LEVEL)]

# # logging configuration
# logging.getLogger().handlers = [InterceptHandler()]
# logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

# Loguru configuration
if settings.USING_DOCKER:
    logger.configure(
        handlers=[{"sink": sys.stderr, "enqueue": True, "level": LOGGING_LEVEL, "format": format_record}]
    )
else:
    logger.configure(
        handlers=[{"sink": sys.stderr, "enqueue": False, "level": LOGGING_LEVEL, "format": format_record}]
    )

# Force all log time in UTC
# https://github.com/Delgan/loguru/issues/338
logger.configure(patcher=set_log_extras)
logger.debug('Logging system initialized')


def get_loggers():
    
    return logger, logging
