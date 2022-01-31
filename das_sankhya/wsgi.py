# -*- coding: utf-8 -*-
"""Application Web Server Gateway Interface - gunicorn."""
import logging
import os
import pytz
import sys
from time import sleep

from gunicorn.app.base import Application
from loguru import logger
from das_sankhya.app.asgi import get_app
from das_sankhya.config.application import settings
from das_sankhya.core.logs2 import global_log_config
from das_sankhya.core.gunicorn_logs import InThread

# from das_sankhya.core.logs import get_loggers

os.environ["TZ"] = "UTC"
utc = pytz.UTC

# app_logger, app_logging = get_loggers()


class ApplicationLoader(Application):
    """Bypasses the class `WSGIApplication."""

    def init(self, parser, opts, args):
        """Class ApplicationLoader object constructor."""
        self.cfg.set("default_proc_name", args[0])

    def load(self):
        """Load application."""
        return get_app()


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


def run_wsgi(host, port, workers):
    """Run gunicorn WSGI with ASGI workers."""
    global_log_config(
        log_level=(logging.DEBUG if (settings.DEBUG) else logging.INFO),
        json=False,
    )
    logger.info("Start gunicorn WSGI with ASGI workers.")
    # sys.argv = [
    #     "--gunicorn",
    #     "-c",
    #     os.path.join(os.path.dirname(__file__), "config/gunicorn.conf.py"),
    #     "-w",
    #     workers,
    #     "-b {host}:{port}".format(
    #         host=host,
    #         port=port,
    #     ),
    # ]
    # sys.argv.append("das_sankhya.app.asgi:application")

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
            # "threads": cpu + 1,  # os.cpu_count() + 1,  # cpu + 1,  # cpu * 2,
            # "reload": True,
            "backlog": 2048,
            "worker_class": "uvicorn.workers.UvicornWorker",
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
        },
        target=some_thread,
    )
    server.start()
    logger.info("message after server start in main thread")
    server.join()
    logger.info("message after server thread join in main thread")
    # ApplicationLoader().run()


if __name__ == "__main__":
    run_wsgi(
        host=os.getenv("FASTAPI_HOST", "127.0.0.1"),
        port=os.getenv("FASTAPI_PORT", "8000"),
        workers=int(os.getenv("FASTAPI_WORKERS", 2)),
    )
