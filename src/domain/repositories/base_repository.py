from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Generic, Tuple

from src.lib.result import Result, Error

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]): 
    @abstractmethod
    async def find_by_id(self, id: str) -> Result[T, Error]: 
        """
            Find an entity by its ID
            
            Args: 
                id: The ID of the entity to find
            
            Returns: 
                Result containing the entity if found, None if not found, or Error on failure
        """
        pass

    @abstractmethod
    async def find_all(
        self, 
        page: int = 1, 
        limit: int = 10
    ) -> Result[Tuple[list[T], int], Error]: 
        """
            Find all entities
            
            Args: 
                page: The page number to retrieve
                limit: The number of entities to retrieve
            
            Returns: 
                Result containing tuple of (list of entities and total count), or Error on failure
        """
        pass
    
    @abstractmethod
    async def delete(self, entity: T) -> Result[T, Error]: 
        """
            Delete an entity
            
            Args: 
                entity: The entity to delete
            
            Returns: 
                Result containing True if deleted, False if not found, or Error on failure
        """
        pass

    @abstractmethod
    async def save(self, entity: T) -> Result[T, Error]: 
        """
            Save an entity
            
            Args: 
                entity: The entity to save
            
            Returns: 
                Result containing the saved entity, or Error on failure
        """
        pass