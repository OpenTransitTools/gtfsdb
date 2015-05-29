import datetime
import logging
log = logging.getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy.orm import relationship, joinedload_all
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Boolean, Integer, Numeric, String

from gtfsdb import config
from gtfsdb.model.base import Base


class StopTime(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_times.txt'

    __tablename__ = 'stop_times'

    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    arrival_time = Column(String(8))
    departure_time = Column(String(8), index=True)
    stop_id = Column(String(255), index=True, nullable=False)
    stop_sequence = Column(Integer, primary_key=True, nullable=False)
    stop_headsign = Column(String(255))
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    shape_dist_traveled = Column(Numeric(20, 10))
    timepoint = Column(Boolean, index=True, default=False)

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
        ''' get the headsign at this stop ... rule is that if stop is empty, use trip headsign '''
        ret_val = self.stop_headsign
        if not ret_val:
            ret_val = self.trip.trip_headsign
        return ret_val

    def get_direction_name(self, def_val="", banned=['Shuttle', 'MAX Shuttle', 'Garage', 'Center Garage', 'Merlo Garage', 'Powell Garage']):
        ''' returns either the headsign (priority) or the route direction name (when banned)
            (as long as one of these names are not banned and not the same name as the route name)
        '''
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
                dir = self.trip.direction_id
                dir = self.trip.route.directions[dir]
                if dir.direction_name and not any([dir.direction_name in s for s in banned]):
                    ret_val = dir.direction_name.lstrip('to ').lstrip('To ')
        except Exception, e:
            log.debug(e)
            pass
        return ret_val

    def is_boarding_stop(self):
        ''' return whether the vehicle that is stopping at this stop, and at this time, is an
            in-revenue vehicle that a customer can actually board...

            pickup_type = 1 - No pickup available

            departure_time = None

            NOTE: in gtfsdb, we NULL out the departure times when the vehicle doesn't
                  pick up anyone (e.g., at route end points, there are no departures...)

            @see: https://developers.google.com/transit/gtfs/reference#stop_times_fields
        '''
        ret_val = True
        if self.pickup_type == 1 or self.departure_time is None:
            ret_val = False
        return ret_val

    @classmethod
    def post_process(cls, db, **kwargs):
        ''' delete all 'depature_time' values that appear for the last stop
            time of a given trip (e.g., the trip ends there, so there isn't a
            further vehicle departure for that stop time / trip pair)...

            NOTE: we know this breaks the current GTFS spec, which states that departure &
                  arrival times must both exist for every stop time.  Sadly, GTFS is wrong...
        '''
        log.debug('{0}.post_process'.format(cls.__name__))

        # remove the departure times at the end of a trip
        log.info("QUERY StopTime")
        sq = db.session.query(StopTime.trip_id, func.max(StopTime.stop_sequence).label('end_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.end_sequence)
        for r in q:
            r.departure_time = None

        # remove the arrival times at the start of a trip
        log.info("QUERY StopTime")
        sq = db.session.query(StopTime.trip_id, func.min(StopTime.stop_sequence).label('start_sequence'))
        sq = sq.group_by(StopTime.trip_id).subquery()
        q = db.session.query(StopTime)
        q = q.filter_by(trip_id=sq.c.trip_id, stop_sequence=sq.c.start_sequence)
        for r in q:
            r.arrival_time = None

        db.session.commit()

    @classmethod
    def get_departure_schedule(cls, session, stop_id, date=None, route_id=None):
        ''' helper routine which returns the stop schedule for a give date
        '''
        from gtfsdb.model.trip import Trip

        # step 0: make sure we have a valid date
        if date is None:
            date = datetime.date.today()

        # step 1: get stop times based on date
        log.info("QUERY StopTime")
        q = session.query(StopTime)
        q = q.filter_by(stop_id=stop_id)
        q = q.filter(StopTime.departure_time != None)
        q = q.filter(StopTime.trip.has(Trip.universal_calendar.any(date=date)))

        # step 2: apply an optional route filter
        if route_id:
            q = q.filter(StopTime.trip.has(Trip.route_id == route_id))

        # step 3: order the stop times
        q = q.order_by(StopTime.departure_time)

        # step 4: options to speed up /q
        q = q.options(joinedload_all('trip'))

        ret_val = q.all()
        return ret_val
