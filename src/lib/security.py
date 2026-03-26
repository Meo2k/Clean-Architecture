import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from config import app_config


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
    to_encode = data.copy()

    # add expire time
    expire = datetime.now(timezone.utc) + timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(data, app_config.ACCESS_TOKEN_KEY, algorithm=app_config.ALGORITHM_HASH)

def verify_access_token(token: str) -> dict | None: 
    try:
        decoded_data = jwt.decode(token, app_config.ACCESS_TOKEN_KEY, algorithms=[app_config.ALGORITHM_HASH])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None

def create_refresh_token(data: dict) -> str: 
    to_encode = data.copy()

    # add expire time
    expire = datetime.now(timezone.utc) + timedelta(days=app_config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    return jwt.encode(data, app_config.REFRESH_TOKEN_KEY, algorithm=app_config.ALGORITHM_HASH)

def verify_refresh_token(token: str) -> dict | None: 
    try:
        decoded_data = jwt.decode(token, app_config.REFRESH_TOKEN_KEY, algorithms=[app_config.ALGORITHM_HASH])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None
