import logging
import cuid
from dataclasses import dataclass
from uuid import UUID, uuid4

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from das_sankhya.middlewares.asgi_correlation_id.context import correlation_id, request_id, idempotency_key
from das_sankhya.middlewares.asgi_correlation_id.extensions.sentry import get_sentry_extension

logger = logging.getLogger('asgi_correlation_id')


def is_valid_uuid(uuid_: str) -> bool:
    """
    Check whether a string is a valid cuid or v4 uuid.
    """
    # Presumed to be a cuid
    if len(uuid_) == 25 and uuid_.lower().startswith('c'):
        return True
    
    # Verify if is valid v4 uuid
    try:
        return bool(UUID(uuid_, version=4))
    except ValueError:
        return False

@dataclass
class CorrelationIdMiddleware:
    app: ASGIApp
    header_name: str = 'X-Correlation-ID'
    validate_header_as_uuid: bool = True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Load request ID from headers if present. Generate one otherwise.
        """
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        header_value = Headers(scope=scope).get(self.header_name.lower())

        if not header_value:
            id_value = cuid.cuid()  # uuid4().hex
        elif self.validate_header_as_uuid and not is_valid_uuid(header_value):
            logger.warning('Generating new CUID, since header value \'%s\' is invalid', header_value)
            id_value = cuid.cuid()  # uuid4().hex
        else:
            id_value = header_value

        correlation_id.set(id_value)
        self.sentry_extension(id_value)

        async def handle_outgoing_request(message: Message) -> None:
            if message['type'] == 'http.response.start':
                headers = {k.decode(): v.decode() for (k, v) in message['headers']}
                headers[self.header_name] = correlation_id.get()
                headers['Access-Control-Expose-Headers'] = self.header_name
                response_headers = Headers(headers=headers)
                message['headers'] = response_headers.raw
            await send(message)

        await self.app(scope, receive, handle_outgoing_request)
        return

    def __post_init__(self) -> None:
        """
        Load extensions on initialization.

        If Sentry is installed, propagate correlation IDs to Sentry events.
        If Celery is installed, propagate correlation IDs to spawned worker processes.
        """
        self.sentry_extension = get_sentry_extension()
        try:
            import celery  # noqa: F401

            from asgi_correlation_id.extensions.celery import load_correlation_ids

            load_correlation_ids()
        except ImportError:  # pragma: no cover
            pass

@dataclass
class RequestIdMiddleware:
    app: ASGIApp
    header_name: str = 'X-Request-ID'
    validate_header_as_uuid: bool = True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Generate new request ID.
        """
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        id_value = cuid.cuid()

        request_id.set(id_value)

        async def handle_outgoing_request(message: Message) -> None:
            if message['type'] == 'http.response.start':
                headers = {k.decode(): v.decode() for (k, v) in message['headers']}
                headers[self.header_name] = request_id.get()
                headers['Access-Control-Expose-Headers'] = self.header_name
                response_headers = Headers(headers=headers)
                message['headers'] = response_headers.raw
            await send(message)

        await self.app(scope, receive, handle_outgoing_request)
        return

    def __post_init__(self) -> None:
        """
        Load extensions on initialization.

        If Sentry is installed, propagate correlation IDs to Sentry events.
        If Celery is installed, propagate correlation IDs to spawned worker processes.
        """
        # self.sentry_extension = get_sentry_extension()
        # try:
        #     import celery  # noqa: F401

        #     from asgi_correlation_id.extensions.celery import load_correlation_ids

        #     load_correlation_ids()
        # except ImportError:  # pragma: no cover
        #     pass
        pass


@dataclass
class IdempotencyKeyMiddleware:
    app: ASGIApp
    header_name: str = 'Idempotency-Key'
    validate_header_as_uuid: bool = True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Get idempotency KEY.
        """
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        header_value = Headers(scope=scope).get(self.header_name.lower())
        if header_value:
            idempotency_key.set(header_value[:128])

        async def handle_outgoing_request(message: Message) -> None:
            if message['type'] == 'http.response.start':
                idk = idempotency_key.get()
                if idk is not None:
                    headers = {k.decode(): v.decode() for (k, v) in message['headers']}
                    headers[self.header_name] = idk
                    # headers['Access-Control-Expose-Headers'] = self.header_name
                    response_headers = Headers(headers=headers)
                    message['headers'] = response_headers.raw
            await send(message)

        await self.app(scope, receive, handle_outgoing_request)
        return

    def __post_init__(self) -> None:
        """
        Load extensions on initialization.

        If Sentry is installed, propagate correlation IDs to Sentry events.
        If Celery is installed, propagate correlation IDs to spawned worker processes.
        """
        # self.sentry_extension = get_sentry_extension()
        # try:
        #     import celery  # noqa: F401

        #     from asgi_correlation_id.extensions.celery import load_correlation_ids

        #     load_correlation_ids()
        # except ImportError:  # pragma: no cover
        #     pass
        pass
