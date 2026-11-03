import os
import socket
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import settings

from src.api.routes import auth_route, user_route, order_route
from src.api.errors import setup_error_handler
from src.core.middleware import LoggingMiddleware
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# Identify this specific instance (useful for verifying Load Balancing)
SERVER_ID = os.getenv("SERVER_ID", socket.gethostname())

app = FastAPI(
    title=settings.SYS_NAME,
    version=settings.VERSION,
)

# Expose Prometheus metrics at /metrics
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics"],
)
instrumentator.add(metrics.requests())
instrumentator.add(metrics.latency())
instrumentator.instrument(app).expose(app, endpoint="/metrics", tags=["Monitoring"])




# origin
origins: list[str] = []

for url in settings.FE_URL:
    if url and url not in origins:
        origins.append(url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

@app.middleware("http")
async def add_server_identity_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Server-ID"] = SERVER_ID
    return response

# setup error handler
setup_error_handler(app)

# include api routes 
app.include_router(auth_route.router, prefix="/api")
app.include_router(user_route.router, prefix="/api")
app.include_router(order_route.router, prefix="/api")

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns simple status to verify the API is running and which instance responded.
    """
    return {
        "status": "healthy",
        "service": settings.SYS_NAME,
        "version": settings.VERSION,
        "server_id": SERVER_ID,
    }

