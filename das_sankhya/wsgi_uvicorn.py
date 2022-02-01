# -*- coding: utf-8 -*-
"""Application Web Server Gateway Interface - uvicorn."""
import logging
import os
import pytz
import sys

# import uvicorn
from uvicorn import Config, Server
import uvicorn
from loguru import logger

from das_sankhya.app.asgi import get_app
from das_sankhya.config.application import settings
from das_sankhya.core.logs2 import global_log_config

# Set time to UTC
# os.environ["TZ"] = "UTC"
# utc = pytz.UTC

# https://stackoverflow.com/questions/68979130/gunicorn-uvicorn-run-programatically-or-via-command-line
def run_dev_wsgi(
    host=os.getenv("FASTAPI_HOST", "127.0.0.1"),
    port=os.getenv("FASTAPI_PORT", "8000"),
    workers=int(os.getenv("FASTAPI_WORKERS", 2)),
):
    """Run uvicorn WSGI with ASGI workers."""
    # THIS NOT LOAD WATCHDOG
    # global_log_config(
    #     log_level=(logging.DEBUG if (settings.DEBUG) else logging.INFO),
    #     json=False,
    # )
    # server = Server(
    #     Config(
    #         "das_sankhya.app.asgi:application",
    #         host=host,
    #         port=int(port),
    #         # workers=int(workers),
    #         reload=True,
    #         lifespan="off",
    #         log_config=None,
    #         access_log=False,
    #     ),
    # )
    # global_log_config(
    #     log_level=(logging.DEBUG if (settings.DEBUG) else logging.INFO),
    #     json=False,
    # )
    # server.run()

    # global_log_config(
    #     log_level=logging.getLevelName(settings.LOG_LEVEL),
    #     json=settings.JSON_LOGS,
    # )
    logger.info("Start uvicorn WSGI with ASGI workers.")
    sys.exit(
        uvicorn.run(
            "das_sankhya.app.asgi:application",
            host=host,
            port=int(port),
            reload=True,
            # Workers are not used when reload = True
            workers=int(workers),
            lifespan="off",
            log_config=None,
            access_log=True,
        )
    )


if __name__ == "__main__":
    run_dev_wsgi(
        host=os.getenv("FASTAPI_HOST", "127.0.0.1"),
        port=os.getenv("FASTAPI_PORT", "8000"),
        workers=int(os.getenv("FASTAPI_WORKERS", 2)),
    )
