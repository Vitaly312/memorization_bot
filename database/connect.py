from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import os
from .models import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "mysql+aiomysql://{user}:{password}@{host}:{port}/{database}".format(
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST", "db"),
    port=os.getenv("MYSQL_PORT", 3306),
    database=os.getenv("MYSQL_DATABASE"),
)
engine = create_async_engine(DATABASE_URL, pool_recycle=1600)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
