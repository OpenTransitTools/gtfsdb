from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID
import uuid


class Frequency(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'frequencies.txt'

    __tablename__ = 'gtfs_frequencies'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    trip_id = Column(GUID())
    start_time = Column(String(8))
    end_time = Column(String(8))
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    trip = relationship(
        'Trip',
        primaryjoin='Frequency.trip_id==Trip.trip_id',
        foreign_keys='(Frequency.trip_id)',
        uselist=False, viewonly=True)
