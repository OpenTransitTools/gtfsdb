from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, ForeignKey, Integer, String

from .trip import Trip


class Frequency(DeclarativeBase):
    __tablename__ = 'frequencies'

    required_fields = ['trip_id', 'start_time', 'end_time', 'headway_secs']
    proposed_fields = ['exact_times']

    trip_id = Column(String, ForeignKey(Trip.trip_id), primary_key=True)
    start_time = Column(String, primary_key=True)
    end_time = Column(String)
    headway_secs = Column(Integer)
    exact_times = Column(Integer)
