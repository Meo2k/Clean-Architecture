from pydantic import BaseModel, Field

from src.api.schemas.base_schema import BaseResponse


class CreateOrderRequest(BaseModel): 
    amount: int

class CreateOrderResponse(BaseResponse): 
    pass

class SepayWebhookPayload(BaseModel):
    gateway: str
    transactionDate: str
    accountNumber: str
    subAccount: str | None = None
    code: str
    content: str
    transferType: str
    description: str
    transferAmount: int
    referenceCode: str
    accumulated: int | None = None
    id: int


class SepayWebhookResponse(BaseModel):
    success: bool
    detail: str | None = None
