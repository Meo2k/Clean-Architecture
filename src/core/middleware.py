import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        client_ip = request.client.host if request.client else "Unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        try:
            response = await call_next(request)
        except Exception:
            process_time = time.time() - start_time
            logger.warning(
                f"{request.method} {request.url.path} "
                f"- Status: 500 (Unhandled) "
                f"- Processing Time: {process_time:.4f}s "
                f"- IP: {client_ip}"
            )
            raise

        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Processing Time: {process_time:.4f}s "
            f"- IP: {client_ip}"
        )
        return response


__all__ = ["LoggingMiddleware"]
