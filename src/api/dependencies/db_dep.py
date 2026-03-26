from sqlalchemy.ext.asyncio import AsyncSession

from config import app_config

from src.infras.services.sql_unit_of_work_service import SQLAlchemyUnitOfWork
from src.infras.storage.engine import create_session_factory

from src.app.services.unit_of_work_service import UnitOfWork


session_factory = create_session_factory(database_url=app_config.DATABASE_URL)


async def get_db_session() -> AsyncSession: 
    """ provide database session """
    session = session_factory()
    try: 
        yield session 
    finally: 
        await session.close() 

def get_unit_of_work() -> UnitOfWork: 
    """ provide unit of work """
    return SQLAlchemyUnitOfWork(session_factory)