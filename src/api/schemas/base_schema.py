from pydantic import BaseModel, Field


class BaseResponse(BaseModel): 
    message: str = Field(..., min_length=3, max_length=255) 

