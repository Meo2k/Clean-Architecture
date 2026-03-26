from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

def create_session_factory(
    database_url: str, 
    max_overflow: int = 20, 
    pool_size: int = 10, 
    echo: bool = False, 
) -> async_sessionmaker[AsyncSession]: 
   """
    Create a session factory for the database.

    Args:
        database_url: The URL of the database.
        max_overflow: The maximum number of connections to allow.
        pool_size: The number of connections to keep in the pool.
        echo: Whether to echo the SQL queries.

    Returns:
        A session factory for the database.
   """
   engine = create_async_engine(
       database_url,
       echo=echo,
       pool_pre_ping=True,
       pool_size=pool_size,
       max_overflow=max_overflow,
   )
   return async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False
   )

def create_worker_session_factory(
    database_url: str,
    echo: bool = False 

) -> async_sessionmaker[AsyncSession]: 
    """
    Create async session factory for background workers.
    Workers don't nedd connection pool since they run indenpendently

    Args:
        database_url: The URL of the database.
        echo: Whether to echo the SQL queries.

    Returns:
        A session factory for the database.
    """
    engine = create_async_engine(
        database_url, 
        poolclass=NonePool, 
        echo=echo 

    )
    return async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
