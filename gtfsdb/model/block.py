import sys
import time

from sqlalchemy import Column, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.trip import Trip

import logging
log = logging.getLogger(__name__)


class Block(Base):
    """
    This is really a BlockTripService table, in that we have entries for each Block / Trip pair, so that we can see
    the order of trips served by a given vehicle (block) for a particular service.

    One purpose is to know which trips might begin and end at a given stop .. we often don't want to show
    'arrival stops' in either our list of RouteStops or Stop Schedule listings...
    """
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'blocks'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    sequence = Column(Integer)
    block_id = Column(String(255), index=True, nullable=False)
    service_id = Column(String(255), index=True, nullable=False)
    trip_id = Column(String(255), index=True, nullable=False)
    prev_trip_id = Column(String(255))
    next_trip_id = Column(String(255))
    start_stop_id = Column(String(255), index=True, nullable=False)
    end_stop_id = Column(String(255), index=True, nullable=False)

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

    start_stop = relationship(
        'Stop',
        primaryjoin='Stop.stop_id==Block.start_stop_id',
        foreign_keys='(Block.start_stop_id)',
        uselist=False, viewonly=True)

    end_stop = relationship(
        'Stop',
        primaryjoin='Stop.stop_id==Block.end_stop_id',
        foreign_keys='(Block.end_stop_id)',
        uselist=False, viewonly=True)

    def __init__(self, sequence, block_id, service_id, trip_id, prev_trip_id, next_trip_id, start_stop_id, end_stop_id):
        self.sequence = sequence
        self.block_id = block_id
        self.service_id = service_id
        self.trip_id = trip_id
        self.prev_trip_id = prev_trip_id
        self.next_trip_id = next_trip_id
        self.start_stop_id = start_stop_id
        self.end_stop_id = end_stop_id

    def is_arrival(self, stop_id=None):
        """
        check whether two sequential trips running on this block first arrive and then depart at this stop...
        if this is an 'arrival' stop, then we probably don't want to show it, etc...
        """
        ret_val = False

        # default is end_stop_id
        if stop_id is None:
            stop_id = self.end_stop_id

        if self.next_trip and self.next_trip.start_stop.stop_id == stop_id:
            # import pdb; pdb.set_trace()
            ret_val = True
        return ret_val

    @classmethod
    def load(cls, db, **kwargs):
        log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))
        pass

    @classmethod
    def post_process(cls, db, **kwargs):
        ignore_blocks = kwargs.get('ignore_blocks', None)
        log.debug('{0} {1}.post_process'.format("skip" if ignore_blocks else "run", cls.__name__))
        if not ignore_blocks:
            cls.populate(db)

    @classmethod
    def populate(cls, db):
        """
        loop thru a full trip table and break things into buckets based on service key and block id
        """
        start_time = time.time()
        batch_size = config.DEFAULT_BATCH_SIZE
        num_recs = 0

        # step 1: loop thru all trips, sorted by block and service key
        trips = db.session.query(Trip).order_by(Trip.block_id, Trip.service_id).all()
        i = 0
        while i < len(trips):
            # make sure the trip has a couple stops
            if not trips[i].is_valid:
                i = i + 1
                continue

            b = trips[i].block_id
            s = trips[i].service_id

            # need block (optional) and service id info ... if we don't have that, continue to next trip
            if b is None or s is None:
                i = i + 1
                continue

            # step 2: grab a batch of trips that have the same block and service id
            t = []
            while i < len(trips):
                if not trips[i].is_valid:
                    i = i + 1
                    continue

                if trips[i].block_id != b or trips[i].service_id != s:
                    break
                t.append(trips[i])
                i = i + 1

            # step 3: sort our bucket
            sorted_blocks = sorted(t, key=lambda t: t.start_time)
            sb_len = len(sorted_blocks) - 1

            # step 4: create block objects
            for j, k in enumerate(sorted_blocks):
                prev = None
                next = None
                if j > 0:
                    prev = sorted_blocks[j - 1].trip_id
                if j < sb_len:
                    next = sorted_blocks[j + 1].trip_id
                block = Block(
                    sequence=j + 1,
                    block_id=b,
                    service_id=s,
                    trip_id=k.trip_id,
                    prev_trip_id=prev,
                    next_trip_id=next,
                    start_stop_id=k.start_stop.stop_id,
                    end_stop_id=k.end_stop.stop_id
                )
                db.session.add(block)

            # step 5: insert in the db
            num_recs = num_recs + sb_len
            if num_recs >= batch_size:
                sys.stdout.write('*')
                db.session.flush()
                db.session.commit()
                num_recs = 0

        # step 5b: (final) insert into the db
        db.session.flush()
        db.session.commit()

        processing_time = time.time() - start_time
        log.debug('{0}.populate ({1:.0f} seconds)'.format(cls.__name__, processing_time))

    @classmethod
    def start_stop_ids(cls, session):
        """
        return an array of distinct starting stop_ids
        """
        ret_val = []
        blocks = session.query(Block).all()
        for b in blocks:
            if b.start_stop_id not in ret_val:
                ret_val.append(b.start_stop_id)
        return ret_val

    @classmethod
    def end_stop_ids(cls, session):
        """
        return an array of distinct ending stop_ids
        """
        ret_val = []
        blocks = session.query(Block).all()
        for b in blocks:
            if b.end_stop_id not in ret_val:
                ret_val.append(b.end_stop_id)
        return ret_val

    @classmethod
    def active_stop_ids(cls, session, limit=None):
        """
        return an array of unique starting and ending stop_ids
        use the dict {'stop_id':id} format for return (compatible with Stops.active_stop_ids())
        """
        stops = cls.start_stop_ids(session)
        stops.extend(cls.end_stop_ids(session))
        unique = set(stops)

        ret_val = []
        for i, s in enumerate(unique):
            if limit and i > int(limit):
                break
            ret_val.append({'stop_id': s})
        return ret_val

    @classmethod
    def blocks_by_stop_id(cls, session, stop_id, trip_id=None, service_keys=None, by_start_stop=False, by_end_stop=False):
        """
        query blocks by stop id and service keys ...
        """
        q = session.query(Block)
        if trip_id:
            q = q.filter(Block.trip_id == trip_id)
        if by_start_stop:
            q = q.filter(Block.start_stop_id == stop_id)
        if by_end_stop:
            q = q.filter(Block.end_stop_id == stop_id)
        if service_keys:
            q = q.filter(Block.service_id.in_(service_keys))
        blocks = q.all()
        return blocks

    @classmethod
    def blocks_by_start_stop_id(cls, session, stop_id, trip_id=None, service_keys=None):
        """
        query blocks by the start stop
        """
        return cls.blocks_by_stop_id(session, stop_id, trip_id=trip_id, service_keys=service_keys, by_start_stop=True)

    @classmethod
    def blocks_by_end_stop_id(cls, session, stop_id, trip_id=None, service_keys=None):
        """
        query blocks by the end stop
        """
        return cls.blocks_by_stop_id(session, stop_id, trip_id=trip_id, service_keys=service_keys, by_end_stop=True)

    @classmethod
    def blocks_by_trip_stop(cls, session, trip_id, stop_id, by_end_stop=True):
        """
        query blocks by the end stop
        """
        if by_end_stop:
            blocks = cls.blocks_by_end_stop_id(session, stop_id, trip_id=trip_id)
        else:
            blocks = cls.blocks_by_start_stop_id(session, stop_id, trip_id=trip_id)

        return blocks
