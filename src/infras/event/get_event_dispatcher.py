from fastapi import BackgroundTasks

from src.infras.event.event_dispatcher import current_bg_tasks
from src.infras.event.event_dispatcher import FastAPIDispatcher
from src.app.event.event_dispatcher import EventDispatcher
from src.infras.event.handlers.order_handler import send_email_for_order
from src.infras.event.handlers.user_handler import send_email_for_password_change

from src.domain.events.order import OrderCreated
from src.domain.events.user import PasswordChangedEvent


# composite root of event dispatcher
dispatcher: EventDispatcher = FastAPIDispatcher()
dispatcher.subscribe(OrderCreated, send_email_for_order)
dispatcher.subscribe(PasswordChangedEvent, send_email_for_password_change)


async def get_event_dispatcher(background_tasks: BackgroundTasks) -> EventDispatcher: 
    current_bg_tasks.set(background_tasks)
    return dispatcher