# -*- coding: utf-8 -*-
"""Ready controller."""
# import logging
from loguru import logger
from typing import Optional, Dict

from fastapi import APIRouter, Header

from das_sankhya.config import settings
from das_sankhya.middlewares.asgi_correlation_id.context import correlation_id
from das_sankhya.utils import RedisClient, AiohttpClient
from das_sankhya.app.models import ReadyResponse, ErrorResponse
from das_sankhya.app.exceptions import HTTPException

router = APIRouter()
# log = logging.getLogger(__name__)


@router.get(
    "/ready",
    tags=["ready"],
    response_model=ReadyResponse,
    summary="Simple health check.",
    status_code=200,
    responses={502: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def readiness_check(idempotency_key: Optional[str] = Header(None)):
    """Run basic application health check.

    If the application is up and running then this endpoint will return simple
    response with status ok. Moreover, if it has Redis enabled then connection
    to it will be tested. If Redis ping fails, then this endpoint will return
    502 HTTP error.
    \f

    Returns:
        response (ReadyResponse): ReadyResponse model object instance.

    Raises:
        HTTPException: If applications has enabled Redis and can not connect
            to it. NOTE! This is the custom exception, not to be mistaken with
            FastAPI.HTTPException class.

    """
    headers: Dict = {}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    headers["x-correlation-id"] = correlation_id.get()

    logger.bind(payload=headers).info("Started GET /ready")
    host = "http://localhost:8000/api/v1/microservice"
    try:
        response = await AiohttpClient.get(host, headers=headers)
    except Exception as ex:
        logger.bind(payload=str(ex)).error(f"Could not connect to {host}")
        raise HTTPException(
            status_code=404,
            content=ErrorResponse(
                code=404, message=f"Could not connect to {host}"
            ).dict(exclude_none=True),
        )
    # print(response.text)
    if settings.USE_REDIS and not await RedisClient.ping():
        logger.error("Could not connect to Redis")
        raise HTTPException(
            status_code=502,
            content=ErrorResponse(code=502, message="Could not connect to Redis").dict(
                exclude_none=True
            ),
        )
    return ReadyResponse(status="ok")


@router.get(
    "/microservice",
    tags=["ready"],
    response_model=ReadyResponse,
    summary="Sample microservice.",
    status_code=200,
    responses={502: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def microservice(idempotency_key: Optional[str] = Header(None)):
    """Run basic application health check.

    If the application is up and running then this endpoint will return simple
    response with status ok. Moreover, if it has Redis enabled then connection
    to it will be tested. If Redis ping fails, then this endpoint will return
    502 HTTP error.
    \f

    Returns:
        response (ReadyResponse): ReadyResponse model object instance.

    Raises:
        HTTPException: If applications has enabled Redis and can not connect
            to it. NOTE! This is the custom exception, not to be mistaken with
            FastAPI.HTTPException class.

    """
    # a = {"host": "https://bol.com.br"}
    # logger.info(f"Started GET /microservice- {a['host']} - {idempotency_key} - {correlation_id.get()}")
    # try:
    #     response = await AiohttpClient.get(a["host"])
    # except Exception as ex:
    #     logger.bind(payload=str(ex)).error(f"Could not connect to {a['host']}")
    #     raise HTTPException(
    #         status_code=404,
    #         content=ErrorResponse(
    #             code=404, message=f"Could not connect to {a['host']}"
    #         ).dict(exclude_none=True),
    #     )
    # print(response.text)
    if settings.USE_REDIS and not await RedisClient.ping():
        logger.error("Could not connect to Redis")
        raise HTTPException(
            status_code=502,
            content=ErrorResponse(code=502, message="Could not connect to Redis").dict(
                exclude_none=True
            ),
        )
    return ReadyResponse(status="ok")
