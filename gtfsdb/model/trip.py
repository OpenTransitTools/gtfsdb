from sqlalchemy import Column, Index
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID


class Trip(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'trips.txt'

    __tablename__ = 'gtfs_trips'

    trip_id = Column(GUID(), primary_key=True, nullable=False)
    route_id = Column(GUID())
    service_id = Column(GUID(), nullable=False)
    trip_headsign = Column(String(255))
    trip_short_name = Column(String(255))
    direction_id = Column(GUID())
    block_id = Column(GUID())
    shape_id = Column(GUID(), nullable=True) # The forgien key here is going to be difficult
    trip_type = Column(String(255))
    bikes_allowed = Column(Integer, default=0)
    wheelchair_accessible = Column(Integer, default=0)

    stop_times = relationship('StopTime', primaryjoin='Trip.trip_id==StopTime.trip_id',
                              foreign_keys='(StopTime.trip_id)', uselist=True, backref='trip', cascade='delete')
    frequencies = relationship('Frequency', primaryjoin='Trip.trip_id==Frequency.trip_id',
                               foreign_keys='(Frequency.trip_id)', cascade='delete')

    calendar = relationship('Calendar', primaryjoin='Trip.service_id==Calendar.service_id',
                            foreign_keys='(Trip.service_id)', cascade='delete')

    shape_points = relationship('Shape', primaryjoin='Trip.shape_id==Shape.shape_id', uselist=True,
                                foreign_keys='(Trip.shape_id)', cascade='delete')

    shape_geom = relationship('ShapeGeom', primaryjoin='Trip.shape_id==ShapeGeom.shape_id',
                                foreign_keys='(Trip.shape_id)', cascade='delete')


    universal_calendar = relationship(
        'UniversalCalendar',
        primaryjoin='Trip.service_id==UniversalCalendar.service_id',
        foreign_keys='(Trip.service_id)',
        uselist=True, cascade='delete')

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


Index('ix_gtfs_trips_trip_id', Trip.trip_id, postgresql_using='hash')
Index('ix_gtfs_trips_route_id', Trip.route_id, postgresql_using='hash')
Index('ix_gtfs_trips_service_id', Trip.service_id, postgresql_using='hash')


