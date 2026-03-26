from fastapi import BackgroundTasks

import asyncio
import contextvars
from typing import Dict, List, Callable, Type

from src.lib.logger import setup_app_level_logger

from src.app.event.event_dispatcher import EventDispatcher
from src.domain.events.base import Event


logging = setup_app_level_logger(__name__)
current_bg_tasks: contextvars.ContextVar[BackgroundTasks] = contextvars.ContextVar("bg_tasks")


class FastAPIDispatcher(EventDispatcher): 
    def __init__(self):
        self.listeners: Dict[Type, List[Callable]] = {}

    def subscribe(self, event_type: Type, listener: Callable): 
        """Subscribe a listener to an event type"""
        if event_type not in self.listeners: 
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def dispatch(self, event: Event): 
        """Dispatch an event to all listeners"""
        bg_tasks = current_bg_tasks.get() 
        
        event_class = type(event)
        if event_class in self.listeners:
            for listener in self.listeners[event_class]:
                bg_tasks.add_task(self._safe_execute, listener, event)

    async def _safe_execute(self, handler: Callable, event: Event): 
        """check if handler is async function, if yes await it, else just call it"""

        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event) 
        except Exception as e:
            logging.error( f"[Event Error] {type(event).__name__} failed in {handler.__name__}: {str(e)}", )