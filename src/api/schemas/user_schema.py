from pydantic import BaseModel, Field


class UserResponse(BaseModel): 
    id: str = Field(...) 
    username: str | None = Field(default=None, min_length=3, max_length=255) 
    email: str = Field(..., min_length=3, max_length=255) 
    status: bool = Field(default=True)
    phone_number: str | None = Field(default=None, min_length=10, max_length=15) 
    avatar_url: str | None = Field(default=None, min_length=3, max_length=255) 
    bio: str | None = Field(default=None, min_length=3, max_length=255)

class UpdateProfileRequest(BaseModel): 
    username: str | None = Field(default=None, min_length=3, max_length=255) 
    phone_number: str | None = Field(default=None, min_length=10, max_length=15) 
    avatar_url: str | None = Field(default=None, min_length=3, max_length=255) 
    bio: str | None = Field(default=None, min_length=3, max_length=255)

