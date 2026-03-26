from abc import ABC, abstractmethod
from typing import Any

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.order_repository import OrderRepository

class UnitOfWork(ABC):
    """
        Unit of Work pattern: manages all repositories and coordinates transactions. 
    """
    user_repo: UserRepository
    order_repo: OrderRepository

    def track_entity(self, entity: Any) -> None:
        """ Track an entity to collect and dispatch its domain events upon commit """
        pass
    

    @abstractmethod 
    async def __aenter__(self): 
        """ Async context manager entry point """
        return self 

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): 
        """ 
            Async context manager exit point
            Automatically rolls back if exception occurs. 
        """
        await self.rollback()

    @abstractmethod 
    async def commit (self): 
        """
            Commit all changes in the current transaction. 
            Should be called explicitly after all repository operations.
        """
        pass

    @abstractmethod 
    async def rollback(self): 
        """ 
            Rollback all changes in the current transaction. 
            Called automatically on exception, but can be called manually. 
        """
        pass

