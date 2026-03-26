from pydantic import BaseModel, Field

from src.api.schemas.base_schema import BaseResponse
from src.api.schemas.user_schema import UserResponse



class SignUpAuthRequest(BaseModel): 
    username: str | None = Field(default=None, min_length=3, max_length=255) 
    email: str = Field(..., min_length=3, max_length=255) 
    password: str = Field(..., min_length=8, max_length=255) 
 

class SignUpAuthResponse(BaseResponse): 
    pass

class LoginAuthRequest(BaseModel): 
    email: str = Field(..., min_length=3, max_length=255) 
    password: str = Field(..., min_length=8, max_length=255) 


class LoginAuthResponse(BaseResponse): 
    access_token: str = Field(..., min_length=3, max_length=255)
    user: UserResponse 

class ChangePasswordAuthRequest(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=255)
    logout_other_devices: bool = Field(default=False)

class ChangePasswordAuthResponse(BaseResponse):
    pass 