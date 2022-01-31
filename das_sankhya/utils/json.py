# -*- coding: utf-8 -*-
import json
from datetime import datetime, date

# Python packages installed through pipenv
import pytz
import pendulum

# Core modules

# Lib modules


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
