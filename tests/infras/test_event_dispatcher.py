import asyncio
import pytest
from dataclasses import dataclass
from src.domain.events.base import Event
from src.infras.event.event_dispatcher import AsyncEventDispatcher


@dataclass
class SampleEvent(Event):
    payload: str


@pytest.mark.asyncio
async def test_async_event_dispatcher_handles_async_and_sync_listeners():
    dispatcher = AsyncEventDispatcher()
    calls = []

    def sync_listener(event: SampleEvent):
        calls.append(f"sync:{event.payload}")

    async def async_listener(event: SampleEvent):
        await asyncio.sleep(0.01)
        calls.append(f"async:{event.payload}")

    dispatcher.subscribe(SampleEvent, sync_listener)
    dispatcher.subscribe(SampleEvent, async_listener)

    event = SampleEvent(payload="hello")
    dispatcher.dispatch(event)

    # Allow asyncio tasks to finish
    await asyncio.sleep(0.05)

    assert "sync:hello" in calls
    assert "async:hello" in calls


@pytest.mark.asyncio
async def test_async_event_dispatcher_safe_execute_handles_exceptions():
    dispatcher = AsyncEventDispatcher()
    calls = []

    def failing_listener(event: SampleEvent):
        raise RuntimeError("Something failed in listener")

    def successful_listener(event: SampleEvent):
        calls.append(event.payload)

    dispatcher.subscribe(SampleEvent, failing_listener)
    dispatcher.subscribe(SampleEvent, successful_listener)

    # Should not raise exception
    dispatcher.dispatch(SampleEvent(payload="ok"))

    await asyncio.sleep(0.05)
    assert calls == ["ok"]
