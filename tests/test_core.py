import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from main import app
from src.core.messages import MESSAGES
from src.core.middleware import LoggingMiddleware
from src.api.errors import global_exception_handler
from src.core.settings import settings


@pytest.mark.asyncio
async def test_global_exception_handler_returns_formatted_500():
    test_app = FastAPI()
    test_app.add_middleware(LoggingMiddleware)
    test_app.add_exception_handler(Exception, global_exception_handler)

    @test_app.get("/trigger-crash")
    async def crash():
        raise RuntimeError("Something blew up unexpectedly")

    transport = ASGITransport(app=test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/trigger-crash", headers={"origin": "http://localhost:3000"})
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL"
        assert data["error"]["message"] == MESSAGES["SYSTEM"]["INTERNAL_ERROR"]
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


@pytest.mark.asyncio
async def test_logging_middleware_logs_forwarded_ip():
    test_app = FastAPI()
    test_app.add_middleware(LoggingMiddleware)

    @test_app.get("/test-ip")
    async def ok():
        return {"status": "ok"}

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/test-ip", headers={"X-Forwarded-For": "203.0.113.195, 70.41.3.18"})
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_setup_error_handler_unified_client_error():
    from src.api.errors import setup_error_handler, ClientError
    from src.core.result import Error

    test_app = FastAPI()
    setup_error_handler(test_app)

    @test_app.get("/client-error")
    async def fail():
        raise ClientError(Error(code="bad_input", message="Invalid parameter"), status_code=400)

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/client-error")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "bad_input"
        assert data["error"]["message"] == "Invalid parameter"
