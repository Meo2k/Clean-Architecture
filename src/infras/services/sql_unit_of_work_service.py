from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from src.infras.repositories.sql_user_repository import SQLUserRepository
from src.infras.repositories.sql_order_repository import SQLOrderRepository

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.event.event_dispatcher import EventDispatcher

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.order_repository import OrderRepository
from src.domain.errors.exceptions import ConcurrentModificationError


class SQLAlchemyUnitOfWork(UnitOfWork): 
    """ Unit of Work implementation for SQLAlchemy with automatic domain event dispatching """

    def __init__(
        self, 
        session_factory: async_sessionmaker[AsyncSession],
        event_dispatcher: EventDispatcher | None = None
    ): 
        self.session_factory = session_factory
        self.event_dispatcher = event_dispatcher
        self.session: AsyncSession | None = None 
        self.user_repo: UserRepository | None = None
        self.order_repo: OrderRepository | None = None
        self._tracked_entities: list[Any] = []

    def track_entity(self, entity: Any) -> None:
        """ Track entity for collecting domain events """
        if entity is not None and entity not in self._tracked_entities:
            self._tracked_entities.append(entity)

    async def __aenter__(self): 
        """
            Context manage entry point: create session and repository
        """
        self.session = self.session_factory()
        self._tracked_entities = []

        # initialize repositories with entity tracking
        self.user_repo = SQLUserRepository(self.session, track_entity=self.track_entity)
        self.order_repo = SQLOrderRepository(self.session, track_entity=self.track_entity)
        
        return self 
    
    async def __aexit__(self, exc_type, exc_val, exc_tb): 
        """
            Context manager exit point: cleanup session
            Automatically rolls back if exception occurs. 
        """
        if exc_type: 
            await self.rollback()
        
        await self.session.close()

    async def commit(self): 
        """
            Commit the transaction 
            if StaleDataError occurs, rollback and raise ConcurrentModificationError -> serve optimistic locking.
            After successful commit, automatically dispatch collected domain events.
        """
        try:
            await self.session.commit()
        except StaleDataError as e:
            await self.session.rollback()
            raise ConcurrentModificationError("Concurrent modification error") from e

        # Automatically dispatch domain events after transaction is committed successfully
        self._dispatch_events()

    async def rollback(self): 
        """ Rollback the transaction and clear tracked events """
        await self.session.rollback()
        for entity in self._tracked_entities:
            if hasattr(entity, "events") and isinstance(entity.events, list):
                entity.events.clear()
        self._tracked_entities.clear()

    def _dispatch_events(self):
        """ Dispatch domain events from all tracked entities and clear them """
        if not self.event_dispatcher:
            return

        for entity in self._tracked_entities:
            if hasattr(entity, "events") and isinstance(entity.events, list):
                while entity.events:
                    event = entity.events.pop(0)
                    self.event_dispatcher.dispatch(event)

        self._tracked_entities.clear()        
        