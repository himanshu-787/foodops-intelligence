import logging
import time

from fastapi import Request

logger = logging.getLogger("foodops")


async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Process-Time-ms"] = f"{duration_ms:.1f}"
    return response