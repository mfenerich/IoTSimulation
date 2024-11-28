from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Temperature(Base):
    __tablename__ = "temperatures"

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(String, nullable=False)
    room_id = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
