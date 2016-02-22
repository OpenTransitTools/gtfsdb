import time
import logging
log = logging.getLogger(__name__)


from sqlalchemy import Column, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.trip import Trip


class Block(Base):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'blocks'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
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

    @classmethod
    def load(cls, db, **kwargs):
        log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))

    @classmethod
    def post_process(cls, db):
        '''
        '''
        start_time = time.time()

        #import pdb; pdb.set_trace()
        session = db.session
        trips = session.query(Trip).all()

        # step 1: for each block...
        for t in trips:
            print t.block_id
            break

        processing_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(cls.__name__, processing_time))
