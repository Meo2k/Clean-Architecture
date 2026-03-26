import uuid6

from src.lib.result import Result, Error, Return
from src.lib.logger import setup_app_level_logger

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.schemas.order_schema import CreateOrderResult, CreateOrderCommand
from src.app.event.event_dispatcher import EventDispatcher

from src.domain.entities.order import Order


logger = setup_app_level_logger(__name__)


class CreateOrderUseCase: 
    def __init__(self, unit_of_work: UnitOfWork, event_dispatcher: EventDispatcher): 
        self.unit_of_work = unit_of_work
        self.event_dispatcher = event_dispatcher

    async def execute(self, command: CreateOrderCommand) -> Result[CreateOrderResult, Error]: 
        logger.info(f"Starting to create order with user id {command.user_id}")
        async with self.unit_of_work as uow: 
            order_repo = uow.order_repo

            # create order and trigger event order created
            new_order = Order.create(
                id=str(uuid6.uuid7()),
                user_id=command.user_id,
                user_email=command.user_email,
                amount=command.amount
            )

            save_result = await order_repo.save(new_order)

            if save_result.is_err():
                await uow.rollback()
                return save_result
            
            

            await uow.commit()
            
            logger.info(f"Order with user id {command.user_id} created successfully")
        
        # handle event
        for event in new_order.events:
            self.event_dispatcher.dispatch(event)
        
        return Return.ok(CreateOrderResult(
                message="Order created successfully"
            ))