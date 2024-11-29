"""
Database models for the FastAPI application.

This module defines the SQLAlchemy ORM models used for database tables, including:
- `Temperature`: Stores temperature readings for rooms in buildings.
- `AvgTemperature`: Stores average temperature values over time intervals.
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Temperature(Base):
    """
    ORM model for the `temperatures` table.

    Attributes:
        id (int): Primary key.
        building_id (str): Identifier for the building.
        room_id (str): Identifier for the room.
        temperature (float): Temperature reading.
        timestamp (datetime): Timestamp of the reading.
    """

    __tablename__ = "temperatures"

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(String, nullable=False)
    room_id = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    timestamp = Column(PG_TIMESTAMP(timezone=True), nullable=False)


class AvgTemperature(Base):
    """
    ORM model for the `avg_temperature_time_interval` table.

    Attributes:
        bucket (datetime): Time bucket for the average temperature.
        building_id (str): Identifier for the building.
        room_id (str): Identifier for the room.
        avg_temp (float): Average temperature for the time interval.
    """

    __tablename__ = "avg_temperature_time_interval"

    bucket = Column(PG_TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    building_id = Column(String, primary_key=True, nullable=False)
    room_id = Column(String, primary_key=True, nullable=False)
    avg_temp = Column(Float, nullable=False)
