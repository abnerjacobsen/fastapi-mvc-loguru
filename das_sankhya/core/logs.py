# Python default modules
import json
import sys, logging
from pprint import pformat
from types import FrameType
from typing import cast

# Python modules installed using pipenv
from loguru import logger
from loguru._defaults import LOGURU_FORMAT  # noqa: WPS436

# App core modules
from das_sankhya.config import settings

# Lib modules
from das_sankhya.utils.json import DateTimeEncoder

# Constants
LOGGING_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "uvicorn.access")

# class InterceptHandler(logging.Handler):
#     def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
#         logger_opt = logger.opt(depth=7, exception=record.exc_info)
#         logger_opt.log(record.levelname, record.getMessage())

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

# class InterceptHandler(logging.Handler):
#     """
#     Default handler from examples in loguru documentaion.
#     See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
#     """

#     def emit(self, record):
#         # Get corresponding Loguru level if it exists
#         try:
#             level = logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno

#         # Find caller from where originated the logged message
#         frame, depth = logging.currentframe(), 2
#         while frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1

#         logger.opt(depth=depth, exception=record.exc_info).log(
#             level, record.getMessage()
#         )


# def format_record(record: dict) -> str:
#     format_string = LOGURU_FORMAT
#     if record["extra"].get("payload") is not None:
#         record["extra"]["payload"] = json.dumps(
#             record["extra"]["payload"], indent=4, ensure_ascii=False, cls=DateTimeEncoder
#         )
#         format_string = "".join((format_string, "\n<level>{extra[payload]}</level>"))
#     format_string = "".join((format_string, "{exception}\n"))
#     return format_string

def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.

    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    format_string = "[{time}] [application_name] [correlationId] [{level}] - {name}:{function}:{line} - {message}"

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
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
logger.debug('Logging system initialized')


def get_loggers():

    return logger, logging
