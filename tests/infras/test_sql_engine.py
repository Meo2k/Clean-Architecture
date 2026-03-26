import pytest
from sqlalchemy.pool import NullPool
from src.infras.storage.sql_engine import create_session_factory, create_worker_session_factory

TEST_DB_URL = "postgresql+asyncpg://user:pass@localhost:5432/testdb"

def test_create_session_factory():
    factory = create_session_factory(TEST_DB_URL)
    assert factory is not None
    assert factory.kw["expire_on_commit"] is False

def test_create_worker_session_factory():
    factory = create_worker_session_factory(TEST_DB_URL)
    assert factory is not None
    sync_engine = factory.kw["bind"].sync_engine
    assert isinstance(sync_engine.pool, NullPool)
