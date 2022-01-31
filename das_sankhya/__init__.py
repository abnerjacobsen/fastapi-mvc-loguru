# -*- coding: utf-8 -*-
"""This project was generated with fastapi-mvc."""
import os
import pytz
from loguru import logger
import logging

from .version import __version__  # noqa: F401

from das_sankhya.config.application import settings
# from das_sankhya.core.logs import get_loggers
# from das_sankhya.core.logs2 import global_config

# Set time to UTC
os.environ["TZ"] = "UTC"
utc = pytz.UTC

# initialize logging
# app_logger, app_logging = get_loggers()

# global_config(log_level=(logging.DEBUG if (settings.DEBUG) else logging.INFO),
#                   json=(not settings.DEBUG))

# log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler())
