from time import perf_counter
from uuid import uuid4

from loguru import logger


class RequestLoggingMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._get_request_id(scope)
        method = scope["method"]
        path = scope["path"]
        started_at = perf_counter()
        status_code = 500

        async def send_with_request_id(message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers

            if (
                message["type"] == "http.response.body"
                and not message.get("more_body", False)
            ):
                self._log_request(
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=status_code,
                    started_at=started_at,
                )

            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            logger.bind(
                request_id=request_id,
                method=method,
                path=path,
                duration_ms=duration_ms,
            ).exception("Request failed")
            raise

    def _get_request_id(self, scope) -> str:
        headers = dict(scope["headers"])
        request_id = headers.get(b"x-request-id")

        if request_id:
            return request_id.decode(errors="ignore")

        return str(uuid4())

    def _log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        started_at: float,
    ) -> None:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)

        logger.bind(
            request_id=request_id,
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
        ).info("Request completed")
