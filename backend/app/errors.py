import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("foodops")


class EmptyCartError(Exception):
    pass


class PaymentFailedError(Exception):
    pass


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(EmptyCartError)
    async def empty_cart_handler(request: Request, exc: EmptyCartError):
        return JSONResponse(status_code=400, content={"error": "EMPTY_CART", "detail": str(exc)})

    @app.exception_handler(PaymentFailedError)
    async def payment_handler(request: Request, exc: PaymentFailedError):
        return JSONResponse(status_code=402, content={"error": "PAYMENT_FAILED", "detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s", request.url.path)   # asli error log mein
        return JSONResponse(status_code=500, content={"error": "INTERNAL_ERROR", "detail": "Something went wrong"})