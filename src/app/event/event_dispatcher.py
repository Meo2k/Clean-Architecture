from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Type

from src.domain.events.base import Event


class EventDispatcher(ABC):
    listeners: Dict[Type, List[Callable]] = {}

    @abstractmethod
    def subscribe(self, event_type: Type, listener: Callable): 
        pass

    @abstractmethod
    def dispatch(self, event: Event): 
        pass