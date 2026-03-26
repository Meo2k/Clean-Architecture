from dataclasses import dataclass

from src.app.schemas.base_schema import BaseResult

@dataclass
class CreateOrderCommand: 
    user_id: str
    user_email: str
    amount: int

@dataclass
class CreateOrderResult(BaseResult): 
    pass
