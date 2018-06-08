import datetime
import logging

from gtfsdb import config
from gtfsdb.model.base import Base
from sqlalchemy import Column
from sqlalchemy.orm import joinedload_all, relationship
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Integer, Numeric, String

log = logging.getLogger(__name__)


class StopTime(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_times.txt'

    __tablename__ = 'stop_times'

    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    stop_id = Column(String(255), index=True, nullable=False)
    stop_sequence = Column(Integer, primary_key=True, nullable=False)
    arrival_time = Column(String(9))
    departure_time = Column(String(9), index=True)
    stop_headsign = Column(String(255))
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    shape_dist_traveled = Column(Numeric(20, 10))
    timepoint = Column(Integer)

    stop = relationship(
        'Stop',
        primaryjoin='Stop.stop_id==StopTime.stop_id',
        foreign_keys='(StopTime.stop_id)',
        uselist=False, viewonly=True)

    trip = relationship(
        'Trip',
        primaryjoin='Trip.trip_id==StopTime.trip_id',
        foreign_keys='(StopTime.trip_id)',
        uselist=False, viewonly=True)

    def __init__(self, *args, **kwargs):
        super(StopTime, self).__init__(*args, **kwargs)
        if 'timepoint' not in kwargs:
            self.timepoint = 'arrival_time' in kwargs

    def get_headsign(self):
        """
        get the headsign at this stop ... rule is that if stop is empty, use trip headsign
        """
        ret_val = self.stop_headsign
        if not ret_val:
            ret_val = self.trip.trip_headsign
        return ret_val

    def get_direction_name(self, def_val="", banned=['Shuttle', 'MAX Shuttle', 'Garage', 'Center Garage', 'Merlo Garage', 'Powell Garage']):
        """
        returns either the headsign (priority) or the route direction name (when banned)
        (as long as one of these names are not banned and not the same name as the route name)
        """
        ret_val = def_val
        try:
            # step 0: create a banned list with the addition of our route_long_name
            banned = banned + [self.trip.route.route_long_name]

            headsign = self.get_headsign()
            if headsign and not any([headsign in s for s in banned]):
                # step 1: use the headsign as the direction name, just as long as the headsign is
                #         not null and not the same as the route name
                ret_val = headsign
            else:
                # step 2: lets use the direction name, if available
                d = self.trip.route.directions[self.trip.direction_id]
                if d.direction_name and not any([d.direction_name in s for s in banned]):
                    ret_val = d.direction_name.lstrip('to ').lstrip('To ')
        except Exception as e:
            log.debug(e)
            pass
        return ret_val

    def is_boarding_stop(self):
        """
        return whether the vehicle that is stopping at this stop, and at this time, is an
        in-revenue vehicle that a customer can actually board...

        pickup_type = 1 - No pickup available

        departure_time = None

        NOTE: in gtfsdb, we NULL out the departure times when the vehicle doesn't
              pick up anyone (e.g., at route end points, there are no departures...)

        @see: https://developers.google.com/transit/gtfs/reference#stop_times_fields
        """
        ret_val = True
        if self.pickup_type == 1 or self.departure_time is None:
            ret_val = False
        return ret_val

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))
        # cls.null_out_last_stop_departures(db) ## commented out due to other processes
        pass

    @classmethod
    def null_out_last_stop_departures(cls, db):
        """
        delete all 'depature_time' values that appear for the last stop
        time of a given trip (e.g., the trip ends there, so there isn't a
        further vehicle departure / customer pickup for that stop time / trip pair)...

        -- query below shows null'd out stop times
        select * from ott.stop_times
        where COALESCE(arrival_time,'')='' or COALESCE(departure_time,'')=''

        NOTE: we know this breaks the current GTFS spec, which states that departure &
              arrival times must both exist for every stop time.  Sadly, GTFS is kinda wrong...
        """
        # step 1: remove the departure times at the end of a trip
        log.info("QUERY StopTime for all trip end times")
        sq = db.session.query(StopTime.trip_id, func.max(StopTime.stop_sequence).label('end_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.end_sequence)
        for st in q:
            if st.pickup_type == 1:
                st.departure_time = None

        # remove the arrival times at the start of a trip
        log.info("QUERY StopTime for all trip start times")
        sq = db.session.query(StopTime.trip_id, func.min(StopTime.stop_sequence).label('start_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.start_sequence)
        for st in q:
            if st.drop_off_type == 1:
                st.arrival_time = None

        db.session.flush()
        db.session.commit()
        db.session.close()

    @classmethod
    def get_service_keys_from_list(cls, stop_times):
        ret_val = []
        for s in stop_times:
            k = s.trip.service_id
            if k not in ret_val:
                ret_val.append(k)
        return ret_val

    @classmethod
    def get_departure_schedule(cls, session, stop_id, date=None, route_id=None, limit=None):
        """
        helper routine which returns the stop schedule for a give date
        """
        from gtfsdb.model.trip import Trip

        # step 0: make sure we have a valid date
        if date is None:
            date = datetime.date.today()

        # step 1: get stop times based on date
        log.debug("QUERY StopTime")
        q = session.query(StopTime)
        q = q.filter_by(stop_id=stop_id)
        q = q.filter(StopTime.departure_time is not None)
        q = q.filter(StopTime.trip.has(Trip.universal_calendar.any(date=date)))

        # step 2: apply an optional route filter
        if route_id:
            q = q.filter(StopTime.trip.has(Trip.route_id == route_id))

        # step 3: options to speed up /q
        q = q.options(joinedload_all('trip'))

        # step 4: order the stop times
        if limit is None or limit > 1:
            q = q.order_by(StopTime.departure_time)

        # step 5: limit results
        if limit:
            q = q.limit(limit)

        stop_times = q.all()
        ret_val = cls.block_filter(session, stop_id, stop_times)

        return ret_val

    @classmethod
    def block_filter(cls, session, stop_id, stop_times):
        """
        we don't want to show stop times that are arrivals, so we look at the blocks and figure out whether
        the input stop is the ending stop, and that there's a next trip starting at this same stop.
        """
        ret_val = stop_times
        if stop_times and len(stop_times) > 1:
            from gtfsdb.model.block import Block
            keys = cls.get_service_keys_from_list(stop_times)
            blocks = Block.blocks_by_end_stop_id(session, stop_id, service_keys=keys)
            if blocks:
                ret_val = []
                for s in stop_times:
                    block = None
                    for b in blocks:
                        if s.trip_id == b.trip_id and s.trip.block_id == b.block_id:
                            block = b
                            blocks.remove(b)
                            break

                    if block is None:
                        ret_val.append(s)
                    elif not block.is_arrival(stop_id):
                            ret_val.append(s)
                            # @todo maybe monkey patch stop_time with block, so we know about last trip

                            # this is an arrival trip, and the next trip
                            # (don't return the stop_time as a departure)
                            # this is the last trip of the day (so return it)
        return ret_val
