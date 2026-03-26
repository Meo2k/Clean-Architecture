from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.events.order import OrderCreated
from src.domain.value_objects.order import OrderStatus
from src.domain.events.base import Event

@dataclass
class Order: 
    """ Aggregate root representing order aggregate """
    id: str
    user_id: str
    amount: int
    status: OrderStatus
    created_at: datetime

    events: list[Event] = field(default_factory=list)

    @classmethod
    def create(
        cls, 
        id: str, 
        user_id: str, 
        user_email: str, 
        amount: int, 
        status: OrderStatus = OrderStatus.PENDING
    ) -> Order: 
        """ create new order and trigger event order created """
        order =  cls(
            id=id,
            user_id=user_id,
            amount=amount,
            status=status,
            created_at=datetime.now()
        )

        # event 
        order.events.append(OrderCreated(
            order_id=order.id,
            user_id=order.user_id,
            user_email=user_email,
            amount=order.amount,
            status=order.status,
            created_at=order.created_at
        ))
        return order
