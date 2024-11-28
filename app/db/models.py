from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Temperature(Base):
    __tablename__ = "temperatures"

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(String, nullable=False)
    room_id = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    timestamp = Column(PG_TIMESTAMP(timezone=True), nullable=False)

class AvgTemperature(Base):
    __tablename__ = "avg_temperature_15min"

    bucket = Column(PG_TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    building_id = Column(String, primary_key=True, nullable=False)
    room_id = Column(String, primary_key=True, nullable=False)
    avg_temp = Column(Float, nullable=False)
