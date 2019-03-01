import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON, UUID

from config import Config

Base = declarative_base()
engine = create_engine(Config.DB_CONNECT_STR)

class Strategy(Base):
    __tablename__ = "strategy"
    id = Column(UUID, primary_key=True)
    name = Column(String(128))
    execution_code = Column(String(10000))
    data_format = Column(String(8))
    subscribes_to = Column(String(1024))
    lookback_period = Column(Integer)
    active = Column(Boolean, default=True)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "execution_code": self.execution_code,
            "data_format": self.data_format,
            "subscribes_to": self.subscribes_to,
            "lookback_period": self.lookback_period,
            "active": self.active
        }


Base.metadata.create_all(engine)
give_session = scoped_session(sessionmaker(bind=engine))
