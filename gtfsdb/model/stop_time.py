from gtfsdb.model import DeclarativeBase
from sqlalchemy import Boolean, Column, Integer, Numeric, Sequence, String


class StopTime(DeclarativeBase):
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

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    trip_id = Column(String, nullable=False)
    arrival_time = Column(String)
    departure_time = Column(String)
    stop_id = Column(String, nullable=False)
    stop_sequence = Column(Integer, nullable=False)
    stop_headsign = Column(String)
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    shape_dist_traveled = Column(Numeric(20,10))
    timepoint = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(StopTime, self).__init__(*args, **kwargs)
        if 'timepoint' not in kwargs:
            self.timepoint = ('arrival_time' in kwargs)
