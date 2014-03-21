from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Trip(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'trips.txt'

    __tablename__ = 'trips'

    route_id = Column(String(255), nullable=False)
    service_id = Column(String(255), nullable=False)
    trip_id = Column(String(255), primary_key=True, nullable=False)
    trip_headsign = Column(String(255))
    trip_short_name = Column(String(255))
    direction_id = Column(Integer)
    block_id = Column(String(255))
    shape_id = Column(String(255), nullable=True)
    trip_type = Column(String(255))
    bikes_allowed = Column(Integer, default=0)
    wheelchair_accessible = Column(Integer, default=0)

    pattern = relationship('Pattern',
        primaryjoin='Trip.shape_id==Pattern.shape_id',
        foreign_keys='(Trip.shape_id)',
        uselist=False, viewonly=True)

    route = relationship('Route',
        primaryjoin='Trip.route_id==Route.route_id',
        foreign_keys='(Trip.route_id)',
        uselist=False, viewonly=True)

    stop_times = relationship('StopTime',
        primaryjoin='Trip.trip_id==StopTime.trip_id',
        foreign_keys='(Trip.trip_id)',
        order_by='StopTime.stop_sequence',
        uselist=True, viewonly=True)

    universal_calendar = relationship('UniversalCalendar',
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
