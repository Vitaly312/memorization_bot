import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from database.models import Base
import datetime
import sqlite3


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()

def adapt_datetime_iso(val):
    """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
    return val.replace(tzinfo=None).isoformat()

sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)

@pytest_asyncio.fixture(scope="session")
def engine() -> AsyncEngine:

    return create_async_engine("sqlite+aiosqlite:///:memory:")

@pytest_asyncio.fixture(scope="session", autouse=True)
async def tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session(engine: AsyncEngine):
    async with engine.begin() as conn:
        SessionMaker = async_sessionmaker(bind=conn)
        session = SessionMaker()
        
        try:
            yield session
        finally:
            await session.close()