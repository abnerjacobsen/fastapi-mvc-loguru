# -*- coding: utf-8 -*-
"""Application Asynchronous Server Gateway Interface."""
import logging
from loguru import logger
import os
import pytz

from fastapi import FastAPI
from das_sankhya.middlewares.asgi_correlation_id import (
    CorrelationIdMiddleware,
    RequestIdMiddleware,
    IdempotencyKeyMiddleware,
)

# from starlette.middleware import Middleware
# from starlette_context.middleware import ContextMiddleware

from das_sankhya.config import router, settings
from das_sankhya.core.logs2 import global_log_config
from das_sankhya.app.middlewares.timing import add_timing_middleware

# from das_sankhya.app.middlewares.request_id import DasRequestIdPlugin
# from das_sankhya.app.middlewares.correlation_id import DasCorrelationIdPlugin
# from das_sankhya.app.middlewares.idempotency_key import DasIdempotencyKeyPlugin
from das_sankhya.utils import RedisClient, AiohttpClient
from das_sankhya.app.exceptions import (
    HTTPException,
    http_exception_handler,
)

os.environ["TZ"] = "UTC"
utc = pytz.UTC

global_log_config(
    log_level=logging.getLevelName(settings.LOG_LEVEL),
    json=settings.JSON_LOGS,
)

# middleware = [
#     Middleware(
#         ContextMiddleware,
#         plugins=(
#             DasIdempotencyKeyPlugin(),
#             # DasRequestIdPlugin(),
#             # DasCorrelationIdPlugin(),
#         ),
#     )
# ]


async def on_startup():
    """Fastapi startup event handler.

    Creates RedisClient and AiohttpClient session.

    """
    logger.info("Execute FastAPI startup event handler.")
    # Initialize utilities for whole FastAPI application without passing object
    # instances within the logic.
    if settings.USE_REDIS:
        await RedisClient.open_redis_client()

    AiohttpClient.get_aiohttp_client()


async def on_shutdown():
    """Fastapi shutdown event handler.

    Destroys RedisClient and AiohttpClient session.

    """
    logger.info("Execute FastAPI shutdown event handler.")
    # Gracefully close utilities.
    if settings.USE_REDIS:
        await RedisClient.close_redis_client()

    await AiohttpClient.close_aiohttp_client()


def get_app():
    """Initialize FastAPI application.

    Returns:
        app (FastAPI): Application object instance.

    """
    logger.debug("Initialize FastAPI application node.")
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        # middleware=middleware,
    )
    logger.debug("Add application routes.")
    app.include_router(router)
    # Register global exception handler for custom HTTPException.
    app.add_exception_handler(HTTPException, http_exception_handler)
    add_timing_middleware(
        app,
        record=logger.info,
    )
    app.add_middleware(IdempotencyKeyMiddleware, header_name="Idempotency-Key")
    app.add_middleware(CorrelationIdMiddleware, header_name="X-Correlation-ID")
    app.add_middleware(RequestIdMiddleware, header_name="X-Request-ID")

    return app


application = get_app()
