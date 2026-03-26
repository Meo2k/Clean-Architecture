from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from src.infras.repositories.user_repository import SQLUserRepository
from src.infras.repositories.order_repository import SQLOrderRepository

from src.app.services.unit_of_work_service import UnitOfWork

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.order_repository import OrderRepository


class SQLAlchemyUnitOfWork(UnitOfWork): 
    """ Unit of Work implementation for SQLAlchemy """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]): 
        self.session_factory = session_factory
        self.session: AsyncSession = None 
        self.user_repo: UserRepository = None
        self.order_repo: OrderRepository = None

    async def __aenter__(self): 
        """
            Context manage entry point: create session and repository
        """
        self.session = self.session_factory()

        # initialize repositories
        self.user_repo = SQLUserRepository(self.session)
        self.order_repo = SQLOrderRepository(self.session)
        
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
            if StaleDataError occurs, rollback and raise ConcurrentModificationError -> serve optimistic locking
        """
        try:
            await self.session.commit()
        except StaleDataError as e:
            await self.session.rollback()
            raise ConcurrentModificationError("Concurrent modification error") from e

    async def rollback(self): 
        """ Rollback the transaction """
        await self.session.rollback()        
        