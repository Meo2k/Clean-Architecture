from dataclasses import dataclass
from datetime import datetime

from src.domain.events.base import Event

from src.domain.value_objects.order import OrderStatus

@dataclass
class OrderCreated(Event): 
    order_id: str
    user_id: str
    user_email: str
    amount: int
    status: OrderStatus
    created_at: datetime