from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from load_config import config
from .models import Base


DATABASE_URL = "mysql+aiomysql://{mysql_user}:{mysql_password}\
@{mysql_host}/{mysql_database}".format(**config["MYSQL"])
engine = create_async_engine(DATABASE_URL, pool_recycle=1600)

async_session = sessionmaker(
    engine, class_=AsyncSession,
)
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def get_conn() -> AsyncSession:
    return async_session()