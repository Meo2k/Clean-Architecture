import json
import asyncio
from datetime import datetime
from typing import Dict, List, Callable, Type, Any
from dataclasses import is_dataclass, asdict

import redis.asyncio as redis
from src.core.logger import setup_app_level_logger
from src.core.settings import settings
from src.app.event.event_dispatcher import EventDispatcher
from src.domain.events.base import Event

logger = setup_app_level_logger(__name__)

class RedisEventDispatcher(EventDispatcher):
    """
    Event Dispatcher using Redis Pub/Sub for inter-service communication
    or distributed background processing.
    """

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.listeners: Dict[str, List[Callable]] = {}
        self._listener_task: Optional[asyncio.Task] = None

    def _event_to_channel(self, event_type: Type) -> str:
        return f"events:{event_type.__name__}"

    def subscribe(self, event_type: Type, listener: Callable):
        channel = self._event_to_channel(event_type)
        if channel not in self.listeners:
            self.listeners[channel] = []
        self.listeners[channel].append(listener)
        logger.info(f"[Redis Event] Subscribed {listener.__name__} to {channel}")

    def dispatch(self, event: Event):
        """
        Publish event to Redis. 
        Note: This is non-blocking as it creates a task for the async publish.
        """
        asyncio.create_task(self._publish(event))

    async def _publish(self, event: Event):
        channel = self._event_to_channel(type(event))
        try:
            # Serialize event
            data = self._serialize_event(event)
            await self.redis_client.publish(channel, json.dumps(data))
            logger.debug(f"[Redis Event] Published to {channel}")
        except Exception as e:
            logger.error(f"[Redis Event] Publish failed: {e}")

    def _serialize_event(self, event: Event) -> Dict[str, Any]:
        if is_dataclass(event):
            data = asdict(event)
        else:
            data = {k: v for k, v in event.__dict__.items() if not k.startswith('_')}
        
        # Handle non-serializable types
        for k, v in data.items():
            if isinstance(v, datetime):
                data[k] = v.isoformat()
        return data

    async def start_listening(self):
        """Start the background task to listen for messages from Redis"""
        if not self.listeners:
            return

        channels = list(self.listeners.keys())
        await self.pubsub.subscribe(*channels)
        
        self._listener_task = asyncio.create_task(self._loop())
        logger.info(f"[Redis Event] Started listening on channels: {channels}")

    async def _loop(self):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = json.loads(message["data"])
                    
                    if channel in self.listeners:
                        for handler in self.listeners[channel]:
                            asyncio.create_task(self._safe_execute(handler, data))
        except Exception as e:
            logger.error(f"[Redis Event] Listener loop error: {e}")

    async def _safe_execute(self, handler: Callable, event_data: Dict[str, Any]):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event_data)
            else:
                handler(event_data)
        except Exception as e:
            logger.error(f"[Redis Event] Handler failed: {e}")

    async def stop(self):
        if self._listener_task:
            self._listener_task.cancel()
        await self.pubsub.unsubscribe()
        await self.redis_client.close()
