from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean, Integer, Numeric, String

from gtfsdb import config
from gtfsdb.model.base import Base


class StopTime(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_times.txt'

    __tablename__ = 'stop_times'

    trip_id = Column(String(255), primary_key=True, nullable=False)
    arrival_time = Column(String(8))
    departure_time = Column(String(8))
    stop_id = Column(String(255), index=True, nullable=False)
    stop_sequence = Column(Integer, primary_key=True, nullable=False)
    stop_headsign = Column(String(255))
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    shape_dist_traveled = Column(Numeric(20, 10))
    timepoint = Column(Boolean, index=True, default=False)

    stop = relationship('Stop',
        primaryjoin='Stop.stop_id==StopTime.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=False, viewonly=True)

    trip = relationship('Trip',
        primaryjoin='Trip.trip_id==StopTime.trip_id',
        foreign_keys='(StopTime.trip_id)',
        uselist=False, viewonly=True)

    def __init__(self, *args, **kwargs):
        super(StopTime, self).__init__(*args, **kwargs)
        if 'timepoint' not in kwargs:
            self.timepoint = 'arrival_time' in kwargs
