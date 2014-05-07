from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Boolean, Integer, Numeric, String

from gtfsdb import config
from gtfsdb.model.base import Base

import logging
log = logging.getLogger(__name__)

class StopTime(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_times.txt'

    __tablename__ = 'stop_times'

    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
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


    @classmethod
    def post_process(cls, db, **kwargs):
        ''' delete all 'depature_time' values that appear for the last stop
            time of a given trip (e.g., the trip ends there, so there isn't a 
            further vehicle departure for that stop time / trip pair) 
        '''
        log.debug('{0}.post_process'.format(cls.__name__))

        # remove the departure times at the end of a trip
        sq = db.session.query(StopTime.trip_id, func.max(StopTime.stop_sequence).label('end_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.end_sequence)
        for r in q:
            r.departure_time = None

        # remove the arrival times at the start of a trip
        sq = db.session.query(StopTime.trip_id, func.min(StopTime.stop_sequence).label('start_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.start_sequence)
        for r in q:
            r.arrival_time = None


        db.session.commit()

