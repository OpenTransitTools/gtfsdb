from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Frequency(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'frequencies.txt'

    __tablename__ = 'frequencies'

    trip_id = Column(
        String(255), ForeignKey('trips.trip_id'), primary_key=True)
    start_time = Column(String(8), primary_key=True)
    end_time = Column(String(8))
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    trip = relationship('Trip')
