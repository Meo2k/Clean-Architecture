from src.infras.event.event_dispatcher import AsyncEventDispatcher
from src.infras.event.redis_dispatcher import RedisEventDispatcher
from src.app.event.event_dispatcher import EventDispatcher
from src.infras.event.handlers.order_handler import send_email_for_order
from src.infras.event.handlers.user_handler import send_email_for_password_change

from src.domain.events.order import OrderCreated
from src.domain.events.user import PasswordChangedEvent
from src.core.settings import settings


# Composition root of event dispatcher
# You can toggle between AsyncEventDispatcher (In-memory) and RedisEventDispatcher
if settings.ENVIRONMENT == "PRODUCTION":
    dispatcher: RedisEventDispatcher = RedisEventDispatcher()
else:
    dispatcher: EventDispatcher = AsyncEventDispatcher()

dispatcher.subscribe(OrderCreated, send_email_for_order)
dispatcher.subscribe(PasswordChangedEvent, send_email_for_password_change)


def get_event_dispatcher() -> EventDispatcher: 
    """Provide the global event dispatcher instance"""
    return dispatcher
