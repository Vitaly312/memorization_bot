import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
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
        SessionMaker = async_sessionmaker(bind=conn, expire_on_commit=False)
        try:
            yield SessionMaker()
        finally:
            await conn.rollback()

@pytest_asyncio.fixture(scope="function")
async def session_manual_commit(engine: AsyncEngine):
    '''
    Fixture for getting a session with deleting all data after test
    '''
    yield AsyncSession(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())