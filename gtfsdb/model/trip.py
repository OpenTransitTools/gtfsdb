from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.route import Route


class Trip(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'trips.txt'

    __tablename__ = 'gtfs_trips'

    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    route_id = Column(String(255), ForeignKey(Route.__tablename__+'.route_id'))
    service_id = Column(String(255), index=True, nullable=False)
    trip_headsign = Column(String(255))
    trip_short_name = Column(String(255))
    direction_id = Column(Integer)
    block_id = Column(String(255))
    shape_id = Column(String(255), index=True, nullable=True) # The forgien key here is going to be difficult
    trip_type = Column(String(255))
    bikes_allowed = Column(Integer, default=0)
    wheelchair_accessible = Column(Integer, default=0)

    stop_times = relationship('StopTime', uselist=True, backref='trip', cascade='delete')

    universal_calendar = relationship(
        'UniversalCalendar',
        primaryjoin='Trip.service_id==UniversalCalendar.service_id',
        foreign_keys='(Trip.service_id)',
        uselist=True, viewonly=True)

    @property
    def end_stop(self):
        return self.stop_times[-1].stop

    @property
    def end_time(self):
        return self.stop_times[-1].arrival_time

    @property
    def start_stop(self):
        return self.stop_times[0].stop

    @property
    def start_time(self):
        return self.stop_times[0].departure_time

    @property
    def trip_len(self):
        return len(self.stop_times)
