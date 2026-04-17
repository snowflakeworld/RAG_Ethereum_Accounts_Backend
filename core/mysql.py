from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# engine = create_engine("mysql+pymysql://root:root@127.0.0.1:3306/ethereum")
# Session = sessionmaker(bind=engine)
# session = Session()


Base = declarative_base()

latestBlockNumber = 24875713


class Variables(Base):
    __tablename__ = "variables"
    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)


def get_variable(key):
    row = session.query(Variables).filter(Variables.key == key).first()

    return row.value
    return latestBlockNumber


def update_variable(key, value):
    row = session.query(Variables).filter(Variables.key == key).first()

    if row:
        row.value = value

    session.commit()

    global latestBlockNumber
    latestBlockNumber = int(value)
