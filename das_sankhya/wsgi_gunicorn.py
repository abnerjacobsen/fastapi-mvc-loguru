# -*- coding: utf-8 -*-
"""Application Web Server Gateway Interface - gunicorn."""
import logging
import os
import pytz
import sys
import signal
from time import sleep

from loguru import logger
from das_sankhya.app.asgi import get_app
from das_sankhya.config.application import settings
from das_sankhya.core.gunicorn_logs import InThread

os.environ["TZ"] = "UTC"
utc = pytz.UTC

server = None


def some_thread():
    logger.info("Message from Thread")
    sleep(10)
    if server is None:
        logger.warning("Server global var is {}".format(server))
    else:

        ## If restart server in function, the variable of server will not work after this
        logger.warning("Restart server")
        server.restart()

        sleep(10)
        logger.warning("End server")
        server.end()


def run_wsgi(host=os.getenv("FASTAPI_HOST", "127.0.0.1"), port=os.getenv("FASTAPI_PORT", "8000"), workers=int(os.getenv("FASTAPI_WORKERS", 2))):
    """Run gunicorn WSGI with ASGI workers."""
    logger.info("Start gunicorn WSGI with ASGI workers.")
    # https://medium.com/building-the-system/gunicorn-3-means-of-concurrency-efbb547674b7
    cpu = os.cpu_count() * 2
    server = InThread(
        get_app(),
        {
            "bind": "{host}:{port}".format(
                host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
                port=os.getenv("FASTAPI_PORT", "8000"),
            ),
            "workers": cpu + 1,  # cpu + 1,  # int(workers),
            "threads": cpu + 1,  # os.cpu_count() + 1,  # cpu + 1,  # cpu * 2,
            "reload": False,
            "backlog": 2048,
            "worker_class": "uvicorn.workers.UvicornWorker",  # "das_sankhya.custom_uvicorn_worker.RestartableUvicornWorker",  # "uvicorn.workers.UvicornWorker",
            "worker_connections": 1000,
            "timeout": 30,
            "keepalive": 2,
            "spew": False,
            "proc_name": settings.PROJECT_NAME,
            "errorlog": "-",
            "accesslog": "-",
            "loglevel": os.getenv("FASTAPI_GUNICORN_LOG_LEVEL", "info"),
            "pidfile": None,
            "umask": 0,
            "user": None,
            "group": None,
            "tmp_upload_dir": None,
            "daemon": False,
            # "worker_int": worker_int,
        },
        target=some_thread,
    )
    server.start()
    server.join()


if __name__ == "__main__":
    run_wsgi(
        host=os.getenv("FASTAPI_HOST", "127.0.0.1"),
        port=os.getenv("FASTAPI_PORT", "8000"),
        workers=int(os.getenv("FASTAPI_WORKERS", 2)),
    )
