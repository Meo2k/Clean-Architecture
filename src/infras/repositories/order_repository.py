from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.result import Result, Error, Return

from src.infras.models.order_model import OrderModel

from src.domain.entities.order import Order
from src.domain.repositories.order_repository import OrderRepository


class SQLOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, order: Order) -> Result[Order, Error]:
        try:
            order_model = OrderModel(
                id=str(order.id),
                user_id=order.user_id,
                amount=order.amount,
                status=order.status,
            )
            self.session.add(order_model)
            await self.session.flush()
            return Return.ok(order)
        except Exception as e:
            return Return.err(Error(code=500, message="Failed to save order", reason=e))