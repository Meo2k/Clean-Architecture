from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import settings

from src.api.routes import auth_route, user_route, order_route
from src.api.errors import setup_error_handler
from src.core.middleware import LoggingMiddleware
from src.infras.event.get_event_dispatcher import get_event_dispatcher, RedisEventDispatcher

app = FastAPI(
    title=settings.SYS_NAME,
    version=settings.VERSION,
)

@app.on_event("startup")
async def startup_event():
    dispatcher = get_event_dispatcher()
    if isinstance(dispatcher, RedisEventDispatcher):
        await dispatcher.start_listening()

@app.on_event("shutdown")
async def shutdown_event():
    dispatcher = get_event_dispatcher()
    if isinstance(dispatcher, RedisEventDispatcher):
        await dispatcher.stop()

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

    Returns simple status to verify the API is running.
    """
    return {
        "status": "healthy",
        "service": settings.SYS_NAME,
        "version": settings.VERSION,
    }
