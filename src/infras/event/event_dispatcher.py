import asyncio
from typing import Dict, List, Callable, Type

from src.core.logger import setup_app_level_logger
from src.app.event.event_dispatcher import EventDispatcher
from src.domain.events.base import Event

logger = setup_app_level_logger(__name__)


class AsyncEventDispatcher(EventDispatcher):

    def __init__(self):
        self.listeners: Dict[Type, List[Callable]] = {}

    def subscribe(self, event_type: Type, listener: Callable):
        """Subscribe a listener to an event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def dispatch(self, event: Event):
        """Dispatch an event to all subscribed listeners asynchronously"""
        event_class = type(event)
        if event_class in self.listeners:
            for listener in self.listeners[event_class]:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self._safe_execute(listener, event))
                except RuntimeError:
                    # Fallback for environments without a running event loop (e.g. sync scripts/tests)
                    asyncio.run(self._safe_execute(listener, event))

    async def _safe_execute(self, handler: Callable, event: Event):
        """Check if handler is an async function, if yes await it, else execute it safely"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(
                f"[Event Error] {type(event).__name__} failed in {handler.__name__}: {str(e)}",
                exc_info=True
            )


# Backward-compatibility alias
FastAPIDispatcher = AsyncEventDispatcher

__all__ = ["AsyncEventDispatcher", "FastAPIDispatcher"]
