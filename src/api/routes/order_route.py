from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from src.api.schemas.order_schema import CreateOrderRequest, CreateOrderResponse
from src.api.routes.error import error_type_handler
from src.api.dependencies.db_dep import get_unit_of_work
from src.api.dependencies.auth_dep import get_current_user

from src.app.use_case.order.create_order_use_case import CreateOrderUseCase
from src.app.services.unit_of_work_service import UnitOfWork
from src.app.schemas.order_schema import CreateOrderCommand
from src.app.event.event_dispatcher import EventDispatcher

from src.lib.logger import setup_app_level_logger


from src.infras.event.get_event_dispatcher import get_event_dispatcher

logger = setup_app_level_logger(__name__)

router = APIRouter(prefix="/order", tags=["Order"])

@router.post(
    "/",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Create a new order with user id, total amount, and status"
)
async def create_order(
    request: CreateOrderRequest, 
    current_user: dict = Depends(get_current_user), 
    unit_of_work: UnitOfWork = Depends(get_unit_of_work), 
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher)
): 
    # mapping 
    command = CreateOrderCommand(
        user_id=current_user["user_id"],
        user_email=current_user["email"],
        amount=request.amount
    )

    logger.info(f"Creating order with user id {command.user_id}")
    
    use_case = CreateOrderUseCase(unit_of_work, event_dispatcher)
    result = await use_case.execute(command)
    
    if result.is_err():     
        error = result.err_value
        logger.error(f"Failed to create order with user id {command.user_id}")
        raise error_type_handler(error, status.HTTP_400_BAD_REQUEST)
    
    # Return success response
    return result.ok_value
    
