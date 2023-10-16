from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from load_config import config
from .models import Base


url = "mysql+mysqlconnector://{mysql_user}:{mysql_password}\
@{mysql_host}/{mysql_database}".format(**config["MYSQL"])
engine = create_engine(url)
engine.connect()
Base.metadata.create_all(engine)

def get_conn() -> Session:
    return Session(bind=engine)