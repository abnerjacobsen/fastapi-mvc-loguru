"""Application routes configuration.

In this file all application endpoints are being defined.
"""
from fastapi import APIRouter
from das_sankhya.config import settings
from das_sankhya.app.controllers.api.v1 import ready

router = APIRouter(prefix="/api/v1")

router.include_router(ready.router, tags=["ready"])
