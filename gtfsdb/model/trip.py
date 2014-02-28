from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Trip(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'trips.txt'

    __tablename__ = 'trips'

    route_id = Column(
        String(255), ForeignKey('routes.route_id'), nullable=False)
    service_id = Column(String(255), nullable=False)
    trip_id = Column(String(255), primary_key=True, nullable=False)
    trip_headsign = Column(String(255))
    trip_short_name = Column(String(255))
    direction_id = Column(Integer)
    block_id = Column(String(255))
    shape_id = Column(
        String(255), ForeignKey('patterns.shape_id'), nullable=True)
    trip_type = Column(String(255))
    trip_bikes_allowed = Column(Integer, default=0)
    wheelchair_accessible = Column(Integer, default=0)

    route = relationship('Route')
    pattern = relationship('Pattern')
    stop_times = relationship('StopTime')
    universal_calendar = relationship('UniversalCalendar',
        primaryjoin='Trip.service_id==UniversalCalendar.service_id',
        foreign_keys='(Trip.service_id)',
        viewonly=True)
