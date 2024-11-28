from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Temperature(Base):
    __tablename__ = "temperatures"

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(String, nullable=False)
    room_id = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    timestamp = Column(PG_TIMESTAMP(timezone=True), nullable=False)  # Updated
