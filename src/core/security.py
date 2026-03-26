import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from src.core.settings import settings


# handler password 

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


# handler jwt


def create_access_token(data: dict) -> str: 
    # add expire time
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {**data, "exp": expire}

    return jwt.encode(to_encode, settings.ACCESS_TOKEN_KEY, algorithm=settings.ALGORITHM_HASH)

def verify_access_token(token: str) -> dict | None: 
    try:
        decoded_data = jwt.decode(token, settings.ACCESS_TOKEN_KEY, algorithms=[settings.ALGORITHM_HASH])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None

def create_refresh_token(data: dict) -> str: 
    # add expire time
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {**data, "exp": expire}
    
    return jwt.encode(to_encode, settings.REFRESH_TOKEN_KEY, algorithm=settings.ALGORITHM_HASH)

def verify_refresh_token(token: str) -> dict | None: 
    try:
        decoded_data = jwt.decode(token, settings.REFRESH_TOKEN_KEY, algorithms=[settings.ALGORITHM_HASH])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None
