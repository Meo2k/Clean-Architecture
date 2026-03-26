from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import app_config

from src.api.routes import auth_route, user_route, order_route
from src.api.routes.error import setup_error_handler

app = FastAPI()

# origin
origins = []

if app_config.FE_URL and app_config.FE_URL not in origins:
    origins.append(app_config.FE_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "service": "instant-node-api",
        "version": "1.0.0"
    }

