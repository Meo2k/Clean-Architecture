from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config import app_config
from src.lib.result import Error, ErrorType

from src.domain.errors.exceptions import (
    ConcurrentModificationError, 
    InvalidEmailOrPasswordError
)


class ClientError(Exception): 
    """
    Client-facing error (4xx status codes).

    Raised when the client made a mistake (bad request, not found, etc.)
    """
    def __init__(self, error: Error, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.error = error
        self.status_code = status_code 

class ServerError(Exception): 
    """
    Server-side error (5xx status codes).

    Raised when something went wrong on our end (database issues, internal logic errors).
    """
    def __init__(self, error: Error, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.error = error
        self.status_code = status_code 

# hander 
def error_type_handler(error: Error, status_code: int):
    if error.error_type == ErrorType.CLIENT:
        return ClientError(error, status_code)
    elif error.error_type == ErrorType.INFRA:
        return ServerError(error)

def client_error_handler(request: Request, exc: ClientError): 
    """
    Handle client errors (4xx).

    Returns error details that are safe to expose to clients.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.error.public()  # Only public error details
    )

def server_error_handler(request: Request, exc: ServerError): 
    """
    Handle server errors (5xx).

    Logs full error details but only returns generic message to client.
    """
    logger.error(f"Server error: {exc.error.to_dict()}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error.code,
            "message": "Internal server error",
            "error_id": exc.error.id  # Include error ID for debugging
        }
    )

def vadiation_error_handler(request: Request, exc: RequestValidationError): 
    """
    Handle FastAPI validation errors (422).

    Triggered when request body/params don't match Pydantic model.
    """
    # missing_fields = [
    #     str(error["loc"][-1]) 
    #     for error in exc.errors() 
    #     if error["type"] == "missing"
    # ]
    
    # if missing_fields:
    #     fields_str = ", ".join(missing_fields)
    #     message = f"{fields_str} is required"
    # else:
    #     message = exc.errors()[0]["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "validation_error",
            "message": "Request validation failed",
            **({"errors": exc.errors()} if app_config.ENVIRONMENT == "DEVELOPMENT" else {})
        }
    )



def concurrent_modification_error_handler(request: Request, exc: ConcurrentModificationError): 
    """
    Handle optimistic lock failures after max retries (409 Conflict).
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error_code": "concurrent_modification",
            "message": str(exc)
        }
    )

def invalid_email_or_password_error_handler(request: Request, exc: InvalidEmailOrPasswordError): 
    """
    Handle invalid email or password errors (401).

    Triggered when user provides invalid email or password.
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error_code": "invalid_email_or_password",
            "message": str(exc)
        }
    )



def setup_error_handler(app: FastAPI): 
    app.add_exception_handler(ClientError, client_error_handler) 
    app.add_exception_handler(ServerError, server_error_handler) 
    app.add_exception_handler(RequestValidationError, vadiation_error_handler) 

    # handle exceptions of domain layer
    app.add_exception_handler(ConcurrentModificationError, concurrent_modification_error_handler) 
    