import cuid
from typing import Optional, Union
from starlette.requests import HTTPConnection, Request
from starlette_context.plugins.base import Plugin
from starlette_context import context
from starlette_context.header_keys import HeaderKeys
from starlette.responses import Response
from starlette.datastructures import MutableHeaders, Headers

class DasIdempotencyKeyPlugin(Plugin):
    key = "Idempotency-Key"

    async def extract_value_from_header_by_key(
            self, request: Union[Request, HTTPConnection]
        ) -> Optional[str]:

            value = await super().extract_value_from_header_by_key(request)

            # # if force_new_uuid or correlation id was not found, create one
            # # if self.force_new_uuid or not value:
            # if not value:
            #     value = self.get_new_uuid()

            # if self.validate:
            #     self.validate_uuid(value)

            return value

    async def enrich_response(self, arg) -> None:
        value = context.get(self.key)
        if value:
            value = str(context.get(self.key))

            # for ContextMiddleware
            if isinstance(arg, Response):
                arg.headers[self.key] = "xxxx" + value
                arg.headers['Access-Control-Expose-Headers'] = self.key
            # for ContextPureMiddleware
            else:
                if arg["type"] == "http.response.start":
                    headers = {k.decode(): v.decode() for (k, v) in arg['headers']}
                    headers[self.header_name] = "ZZZZZZ" + value
                    headers['Access-Control-Expose-Headers'] = self.key
                    response_headers = Headers(headers=headers)
                    arg['headers'] = response_headers.raw

                    # headers['Access-Control-Expose-Headers'] = self.key
                    # headers = MutableHeaders(scope=arg)
                    # headers.append(self.key, value)