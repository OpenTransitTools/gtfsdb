from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from gtfsdb.model.base import Base


class Trip(Base):
    __tablename__ = 'trips'

    required_fields = ['route_id', 'service_id', 'trip_id']
    optional_fields = [
        'trip_headsign',
        'trip_short_name',
        'direction_id',
        'block_id',
        'shape_id'
    ]
    proposed_fields = ['trip_type', 'trip_bikes_allowed']

    route_id = Column(String, ForeignKey('routes.route_id'), nullable=False)
    service_id = Column(String, nullable=False)
    trip_id = Column(String, primary_key=True, nullable=False)
    trip_headsign = Column(String)
    trip_short_name = Column(String)
    direction_id = Column(Integer)
    block_id = Column(String)
    shape_id = Column(String, ForeignKey('patterns.shape_id'), nullable=True)
    trip_type = Column(String)
    trip_bikes_allowed = Column(Integer)

    route = relationship('Route')
    pattern = relationship('Pattern')
    stop_times = relationship('StopTime')
    universal_calendar = relationship('UniversalCalendar',
        primaryjoin='Trip.service_id==UniversalCalendar.service_id',
        foreign_keys=(service_id),
        viewonly=True)
