from src.lib.logger import setup_app_level_logger

from src.domain.events.order import OrderCreated

logger = setup_app_level_logger(__name__)


async def send_email_for_order(event: OrderCreated): 
    logger.info(f"[Event] OrderCreated event dispatched for order: {event.order_id} to user: {event.user_email}")
