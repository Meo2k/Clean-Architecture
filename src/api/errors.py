from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.core.settings import settings
from src.core.logger import logger
from src.core.messages import MESSAGES
from src.core.result import Error, ErrorType
from src.domain.errors.exceptions import (
    ConcurrentModificationError,
    InvalidEmailOrPasswordError,
)


class ClientError(Exception):
    """Client-facing error (4xx status codes)."""
    def __init__(self, error: Error, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.error = error
        self.status_code = status_code


class ServerError(Exception):
    """Server-side error (5xx status codes)."""
    def __init__(self, error: Error, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.error = error
        self.status_code = status_code


def error_type_handler(error: Error, status_code: int) -> Exception:
    """Helper for routes to convert Result Error to appropriate HTTP Exception."""
    if error.error_type == ErrorType.CLIENT:
        return ClientError(error, status_code)
    elif error.error_type == ErrorType.INFRA:
        return ServerError(error)
    return ClientError(error, status_code)


def _cors_headers(request: Request) -> dict:
    origin = request.headers.get("origin", "*")
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }


def _is_dev() -> bool:
    env = getattr(settings, "ENVIRONMENT", "DEVELOPMENT")
    return str(env).lower() == "development"


async def client_error_handler(request: Request, exc: ClientError) -> JSONResponse:
    """Handle client errors (4xx)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error.code,
                "message": exc.error.message,
                "details": str(exc.error.reason) if _is_dev() and exc.error.reason else None,
            },
        },
        headers=_cors_headers(request),
    )


async def server_error_handler(request: Request, exc: ServerError) -> JSONResponse:
    """Handle server errors (5xx) produced by Result Pattern INFRA errors."""
    logger.error(f"Server error: {exc.error.to_dict()}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error.code or "INTERNAL",
                "message": MESSAGES["SYSTEM"]["INTERNAL_ERROR"],
                "details": str(exc.error.reason) if _is_dev() and exc.error.reason else None,
            },
        },
        headers=_cors_headers(request),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors (422)."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu yêu cầu không hợp lệ.",
                "details": exc.errors() if _is_dev() else None,
            },
        },
        headers=_cors_headers(request),
    )


async def concurrent_modification_error_handler(
    request: Request, exc: ConcurrentModificationError
) -> JSONResponse:
    """Handle optimistic lock failures (409 Conflict)."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": {
                "code": "CONCURRENT_MODIFICATION",
                "message": "Dữ liệu đã bị thay đổi bởi thao tác khác, vui lòng thử lại.",
                "details": str(exc) if _is_dev() else None,
            },
        },
        headers=_cors_headers(request),
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for any unhandled exceptions (500)."""
    logger.error(f"Global Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL",
                "message": MESSAGES["SYSTEM"]["INTERNAL_ERROR"],
                "details": str(exc) if _is_dev() else None,
            },
        },
        headers=_cors_headers(request),
    )


def setup_error_handler(app: FastAPI) -> None:
    """Consolidated error handlers setup."""
    app.add_exception_handler(ClientError, client_error_handler)
    app.add_exception_handler(ServerError, server_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(ConcurrentModificationError, concurrent_modification_error_handler)
    app.add_exception_handler(Exception, global_exception_handler)


__all__ = [
    "ClientError",
    "ServerError",
    "error_type_handler",
    "setup_error_handler",
    "global_exception_handler",
    "client_error_handler",
    "server_error_handler",
    "validation_error_handler",
    "concurrent_modification_error_handler",
]
