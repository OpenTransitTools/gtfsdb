from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb.model.base import Base


class Frequency(Base):
    __tablename__ = 'frequencies'

    required_fields = ['trip_id', 'start_time', 'end_time', 'headway_secs']
    proposed_fields = ['exact_times']

    trip_id = Column(String, ForeignKey('trips.trip_id'), primary_key=True)
    start_time = Column(String, primary_key=True)
    end_time = Column(String)
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    trip = relationship('Trip')
