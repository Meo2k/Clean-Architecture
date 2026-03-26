
from dataclasses import dataclass
from src.app.schemas.user_schema import UserResult
from src.app.schemas.base_schema import BaseResult

@dataclass
class SignUpCommand: 
    username: str | None
    email: str
    password: str

@dataclass
class LoginCommand: 
    email: str
    password: str

@dataclass
class SignUpResult(BaseResult): 
    pass

@dataclass
class LoginResult(BaseResult): 
    access_token: str
    refresh_token: str
    user: UserResult

@dataclass
class ChangePasswordCommand:
    user_id: str
    old_password: str
    new_password: str
    logout_other_devices: bool = False

@dataclass
class ChangePasswordResult(BaseResult):
    pass