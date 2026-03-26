from fastapi import Depends

from src.infras.storage.sql_engine import session_factory
from src.infras.services.sql_unit_of_work_service import SQLAlchemyUnitOfWork
from src.infras.event.get_event_dispatcher import get_event_dispatcher

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.event.event_dispatcher import EventDispatcher


def get_unit_of_work(
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher)
) -> UnitOfWork: 
    """Provide unit of work with event dispatcher attached"""
    return SQLAlchemyUnitOfWork(session_factory, event_dispatcher=event_dispatcher)
