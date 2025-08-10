from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from load_config import config
from .models import Base


DATABASE_URL = "mysql+aiomysql://{mysql_user}:{mysql_password}\
@{mysql_host}/{mysql_database}".format(**config["MYSQL"])
engine = create_async_engine(DATABASE_URL, pool_recycle=1600)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
