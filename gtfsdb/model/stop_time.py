from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean, Integer, Numeric, String

from gtfsdb.model.base import Base


class StopTime(Base):
    __tablename__ = 'stop_times'

    required_fields = [
        'trip_id',
        'arrival_time',
        'departure_time',
        'stop_id',
        'stop_sequence'
    ]
    optional_fields = [
        'stop_headsign',
        'pickup_type',
        'drop_off_type',
        'shape_dist_traveled'
    ]
    proposed_fields = ['timepoint']

    trip_id = Column(
        String, ForeignKey('trips.trip_id'), primary_key=True, nullable=False)
    arrival_time = Column(String)
    departure_time = Column(String)
    stop_id = Column(
        String, ForeignKey('stops.stop_id'), index=True, nullable=False)
    stop_sequence = Column(Integer, primary_key=True, nullable=False)
    stop_headsign = Column(String)
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    shape_dist_traveled = Column(Numeric(20, 10))
    timepoint = Column(Boolean, index=True, default=False)

    route = relationship('Route', secondary='trips')
    stop = relationship('Stop')
    trip = relationship('Trip')

    def __init__(self, *args, **kwargs):
        super(StopTime, self).__init__(*args, **kwargs)
        if 'timepoint' not in kwargs:
            self.timepoint = 'arrival_time' in kwargs
