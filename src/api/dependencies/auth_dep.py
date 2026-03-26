from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.lib.result import Error
from src.lib.security import verify_access_token

from src.api.routes.error import ClientError

# tokenUrl is the url of the endpoint that returns the token 
# in swagger ui, it will show the login endpoint to get the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
        Dependency get current user, if token is invalid or expired, raise HTTPException
    """
    payload = verify_access_token(token)
    
    if payload is None:
        raise ClientError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error=Error(
                code="unauthorized",
                message="Token is invalid or expired",
            ),
        )
        
    return payload


# admin 

# telegram bot 