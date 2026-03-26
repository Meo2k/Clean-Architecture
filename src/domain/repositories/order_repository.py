from abc import ABC, abstractmethod

from src.lib.result import Result, Error

from src.domain.entities.order import Order

class OrderRepository(ABC): 
    
    @abstractmethod
    async def save(self, order: Order) -> Result[Order, Error]: 
        """ Save an order to the database. """
        pass 