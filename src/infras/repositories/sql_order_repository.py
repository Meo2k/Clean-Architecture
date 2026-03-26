import uuid
from typing import Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.result import Result, Error, Return, ErrorType

from src.infras.models.order_model import OrderModel

from src.domain.entities.order import Order
from src.domain.repositories.order_repository import OrderRepository


class SQLOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession, track_entity: Callable[[Any], None] | None = None):
        self.session = session
        self.track_entity = track_entity

    async def save(self, order: Order) -> Result[Order, Error]:
        try:
            order_model = self._to_model(order)
            self.session.add(order_model)
            await self.session.flush()

            if self.track_entity:
                self.track_entity(order)

            return Return.ok(self._to_domain(order_model))
        except Exception as e:
            return Return.err(Error(
                code="save_order_error",
                message="Failed to save order",
                error_type=ErrorType.INFRA,
                reason=str(e),
            ))

    @staticmethod
    def _to_domain(order: OrderModel) -> Order:
        return Order(
            id=str(order.id),
            user_id=str(order.user_id),
            amount=order.amount,
            status=order.status,
            created_at=order.created_at,
        )

    @staticmethod
    def _to_model(order: Order) -> OrderModel:
        return OrderModel(
            id=order.id if isinstance(order.id, uuid.UUID) else uuid.UUID(str(order.id)),
            user_id=order.user_id if isinstance(order.user_id, uuid.UUID) else uuid.UUID(str(order.user_id)),
            amount=order.amount,
            status=order.status,
            created_at=order.created_at,
        )