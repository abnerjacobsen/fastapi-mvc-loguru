# -*- coding: utf-8 -*-
"""Application Web Server Gateway Interface - uvicorn."""
import logging
import os
import pytz
import sys
# import uvicorn
from uvicorn import Config, Server
from loguru import logger

from das_sankhya.app.asgi import get_app
from das_sankhya.config.application import settings
from das_sankhya.core.logs2 import global_log_config

# Set time to UTC
os.environ["TZ"] = "UTC"
utc = pytz.UTC

LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])

# setup_logging()
# https://stackoverflow.com/questions/68979130/gunicorn-uvicorn-run-programatically-or-via-command-line
def run_dev_wsgi(host, port, workers):
    """Run uvicorn WSGI with ASGI workers."""
    global_log_config(
        log_level=(logging.DEBUG if (settings.DEBUG) else logging.INFO),
        json=(not settings.DEBUG),
    )

    server = Server(
        Config(
            "das_sankhya.app.asgi:application",
            host=host,
            port=int(port),
            workers=int(workers),
            reload=True,
            lifespan="off",
            log_config=None,
            access_log=False
        ),
    )
    server.run()
    logger.info("Start uvicorn WSGI with ASGI workers.")
    # sys.exit(
    #     uvicorn.run(
    #         "das_sankhya.app.asgi:application",
    #         host=host,
    #         port=int(port),
    #         reload=True,
    #         workers=int(workers),
    #         lifespan="off",
    #         log_level="info",
    #         access_log=False,
    #     )
    # )


if __name__ == "__main__":
    run_dev_wsgi(
        host=os.getenv("FASTAPI_HOST", "127.0.0.1"),
        port=os.getenv("FASTAPI_PORT", "8000"),
        workers=int(os.getenv("FASTAPI_WORKERS", 2)),
    )
