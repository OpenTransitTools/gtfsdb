from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Block(Base):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'blocks'

    block_id = Column(String(255),   index=True, nullable=False)
    trip_id = Column(String(255),    index=True, nullable=False)
    service_id = Column(String(255), index=True, nullable=False)
    prev_trip_id = Column(String(255))
    next_trip_id = Column(String(255))

    universal_calendar = relationship(
        'UniversalCalendar',
        primaryjoin='Block.service_id==UniversalCalendar.service_id',
        foreign_keys='(Block.service_id)',
        uselist=True, viewonly=True)

    trip = relationship(
        'Trip',
        primaryjoin='Block.trip_id==Trip.trip_id',
        foreign_keys='(Block.trip_id)',
        uselist=False, viewonly=True)

    next_trip = relationship(
        'Trip',
        primaryjoin='Block.next_trip_id==Trip.trip_id',
        foreign_keys='(Block.next_trip_id)',
        uselist=False, viewonly=True)

    prev_trip = relationship(
        'Trip',
        primaryjoin='Block.prev_trip_id==Trip.trip_id',
        foreign_keys='(Block.prev_trip_id)',
        uselist=False, viewonly=True)