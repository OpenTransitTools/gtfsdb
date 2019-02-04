import sys
import time

from sqlalchemy import Column, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Date, Integer, String

from gtfsdb import config, util
from gtfsdb.model.base import Base
from .route_stop_base import RouteStopBase

import logging
log = logging.getLogger(__name__)


class RouteStop(Base, RouteStopBase):
    datasource = config.DATASOURCE_DERIVED
    __tablename__ = 'route_stops'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    route_id = Column(String(255), index=True, nullable=False)
    direction_id = Column(Integer, index=True, nullable=False)
    stop_id = Column(String(255), index=True, nullable=False)
    order = Column(Integer, index=True, nullable=False)
    start_date = Column(Date, index=True, nullable=False)
    end_date = Column(Date, index=True, nullable=False)

    route = relationship(
        'Route',
        primaryjoin='RouteStop.route_id==Route.route_id',
        foreign_keys='(RouteStop.route_id)',
        uselist=False, viewonly=True, lazy='joined')

    stop = relationship(
        'Stop',
        primaryjoin='RouteStop.stop_id==Stop.stop_id',
        foreign_keys='(RouteStop.stop_id)',
        uselist=False, viewonly=True, lazy='joined')

    direction = relationship(
        'RouteDirection',
        primaryjoin='RouteStop.route_id==RouteDirection.route_id and RouteStop.direction_id==RouteDirection.direction_id',
        foreign_keys='(RouteStop.route_id, RouteStop.direction_id)',
        uselist=False, viewonly=True, lazy='joined')

    start_calendar = relationship(
        'UniversalCalendar',
        primaryjoin='RouteStop.start_date==UniversalCalendar.date',
        foreign_keys='(RouteStop.start_date)',
        uselist=True, viewonly=True)

    end_calendar = relationship(
        'UniversalCalendar',
        primaryjoin='RouteStop.end_date==UniversalCalendar.date',
        foreign_keys='(RouteStop.end_date)',
        uselist=True, viewonly=True)

    def is_active(self, date=None):
        """
        :return False whenever we see that the route_stop's start and end date are
                outside the input date (where the input date defaults to 'today')
        """
        _is_active = False
        if self.start_date and self.end_date:
            date = util.check_date(date)
            if self.start_date <= date <= self.end_date:
                _is_active = True
        return _is_active

    def is_valid(self):
        ret_val = True
        if self.start_date is None or self.end_date is None:
            ret_val = False
        return ret_val

    def get_id(self):
        ret_val = "r:{0} d:{1} s:{2}".format(self.route_id, self.direction_id, self.stop_id)
        return ret_val

    @classmethod
    def is_stop_active(cls, session, stop_id, agency_id=None, date=None):
        """
        returns boolean whether given stop id is active for a given date
        """
        ret_val = False
        rs = RouteStop.query_by_stop(session, stop_id, agency_id, date, 1)
        if rs and len(rs) > 0:
            ret_val = True
        return ret_val

    @classmethod
    def active_unique_routes_at_stop(cls, session, stop_id, agency_id=None, date=None, route_name_filter=False):
        """
        to filter active routes, just provide a date to the above unique_routes_at_stop method
        """
        ret_val = []
        routes = cls.unique_routes_at_stop(session, stop_id, agency_id, date, route_name_filter)
        for r in routes:
            if r.is_active(date):
                ret_val.append(r)
        return ret_val

    @classmethod
    def query_active_stops(cls, session, route_id, direction_id=None, agency_id=None, date=None):
        """
        returns list of routes that are seen as 'active' based on dates and filters
        """
        # import pdb; pdb.set_trace()

        # step 1: default date
        date = util.check_date(date)

        # step 2a: query all route stops by route (and maybe direction and agency
        q = session.query(RouteStop).filter(RouteStop.route_id == route_id)
        if direction_id is not None:
            q = q.filter(RouteStop.direction_id == direction_id)
        if agency_id is not None:
            pass
            # TODO ... agency_id not in RouteStop -- should this even be here?
            # q = q.filter(RouteStop.agency_id == agency_id)

        # step 2b: filter based on date
        q = q.filter(RouteStop.start_date <= date).filter(date <= RouteStop.end_date)

        # step 2c: add some stop order
        q = q.order_by(RouteStop.order)

        route_stops = q.all()
        return route_stops

    @classmethod
    def load(cls, db, **kwargs):
        log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))
        pass

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))
        cls.populate(db.session)

    @classmethod
    def populate(cls, session):
        """
        for each route/direction, find list of stop_ids for route/direction pairs

        the load is a two part process, where part A finds a list of unique stop ids, and
        part B creates the RouteStop (and potentially RouteDirections ... if not in GTFS) records
        """
        from gtfsdb import Route, RouteDirection

        start_time = time.time()
        routes = session.query(Route).all()

        for r in routes:
            # step 0: figure out some info about the route
            create_directions = False
            if r.directions is None or len(r.directions) == 0:
                create_directions = True

            # step 1a: filter the list of trips down to only a trip with a unique pattern
            trips = []
            shape_id_filter = []
            for t in r.trips:
                # a bit of a speedup to filter trips that have the same shape
                if t.shape_id and t.shape_id in shape_id_filter:
                    continue
                # store our trips
                shape_id_filter.append(t.shape_id)
                trips.append(t)

            # step 1b: sort our list of trips by length (note: for trips with two directions, ...)
            trips = sorted(trips, key=lambda t: t.trip_len, reverse=True)

            # step 2: get a hash table of route stops with effective start and end dates
            stop_effective_dates = cls._find_route_stop_effective_dates(session, r.route_id)

            # PART A: we're going to just collect a list of unique stop ids for this route / directions
            for d in [0, 1]:
                unique_stops = []

                # step 3: loop through all our trips and their stop times, pulling out a unique set of stops
                for t in trips:
                    if t.direction_id == d:

                        # step 4: loop through this trip's stop times, and find any/all stops that are in our stop list already
                        #         further, let's try to find the best position of that stop (e.g., look for where the stop patterns breaks)
                        last_pos = None
                        for i, st in enumerate(t.stop_times):
                            # step 5a: make sure this stop that customers can actually board...
                            if st.is_boarding_stop():

                                # step 5b: don't want arrival trips to influence route stop list
                                if st.stop_id in unique_stops:
                                    last_pos = unique_stops.index(st.stop_id)
                                else:
                                    # step 5b: add ths stop id to our unique list ... either in position, or appended to the end of the list
                                    if last_pos:
                                        last_pos += 1
                                        unique_stops.insert(last_pos, st.stop_id)
                                    else:
                                        unique_stops.append(st.stop_id)

                # PART B: add records to the database ...
                if len(unique_stops) > 0:

                    # step 6: if an entry for the direction doesn't exist, create a new
                    #         RouteDirection record and add it to this route
                    if create_directions:
                        rd = RouteDirection()
                        rd.route_id = r.route_id
                        rd.direction_id = d
                        rd.direction_name = "Outbound" if d == 0 else "Inbound"
                        session.add(rd)

                    # step 7: create new RouteStop records
                    for k, stop_id in enumerate(unique_stops):
                        # step 7: create a RouteStop record
                        rs = RouteStop()
                        rs.route_id = r.route_id
                        rs.direction_id = d
                        rs.stop_id = stop_id
                        rs.order = k + 1
                        s, e = cls._get_stop_effective_dates(stop_effective_dates, stop_id)
                        rs.start_date = s
                        rs.end_date = e
                        if rs.is_valid():
                            session.add(rs)
                        else:
                            log.info("{0} is not valid ... not adding to the database".format(rs.get_id()))

            # step 8: commit the new records to the db for this route...
            sys.stdout.write('*')
            session.commit()

        # step 9: final commit for any stragglers
        session.commit()
        session.flush()
        session.close()

        processing_time = time.time() - start_time
        log.debug('{0}.post_process ({1:.0f} seconds)'.format(cls.__name__, processing_time))

    @classmethod
    def _find_route_stop_effective_dates(cls, session, route_id):
        """
        find effective start date and end date for all stops of the input route, when
        queried against the trip and stop time tables.  Below are a couple of pure SQL queries that
        perform what I'm doing to get said start and end dates:

        # query all route stops with start & end dates
        SELECT t.route_id, st.stop_id, min(date), max(date)
        FROM ott.universal_calendar u, ott.trips t, ott.stop_times st
        WHERE t.service_id = u.service_id
          AND t.trip_id    = st.trip_id
        GROUP BY t.route_id, st.stop_id

        # query all stops start & end dates for a given route (used below in SQLAlchemy)
        SELECT st.stop_id, min(date), max(date)
        FROM ott.universal_calendar u, ott.trips t, ott.stop_times st
        WHERE t.service_id = u.service_id
          AND t.trip_id    = st.trip_id
          AND st.stop_id   = '1'
        GROUP BY st.stop_id

        :return hash table with stop_id as key, and tuple of (stop_id, start_date, end_date) for all route stops
        """
        ret_val = {}

        # step 1: query the route/stop start and end dates, based on stop time table
        from gtfsdb import UniversalCalendar, StopTime, Trip
        q = session.query(StopTime.stop_id, func.min(UniversalCalendar.date), func.max(UniversalCalendar.date))
        q = q.filter(UniversalCalendar.service_id == Trip.service_id)
        q = q.filter(Trip.trip_id  == StopTime.trip_id)
        q = q.filter(Trip.route_id == route_id)
        q = q.group_by(StopTime.stop_id)
        stop_dates = q.all()

        # step 2: make a hash of these dates with the stop id as the key
        for d in stop_dates:
            ret_val[d[0]] = d

        return ret_val

    @classmethod
    def _get_stop_effective_dates(cls, effective_dates_list, stop_id):
        """
        :return: start & end date from the route stop dates returned by method above
        :see: _find_route_stop_effective_dates
        """
        start = None
        end = None
        try:
            start = effective_dates_list[stop_id][1]
            end = effective_dates_list[stop_id][2]
        except Exception as e:
            log.info(e)
        return start, end


class CurrentRouteStops(Base, RouteStopBase):
    """
    this table is (optionally) used as a view into the currently active routes
    it is pre-calculated to list routes that are currently running service
    (GTFS can have multiple instances of the same route, with different aspects like name and direction)
    """
    datasource = config.DATASOURCE_DERIVED
    __tablename__ = 'current_route_stops'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    rs = relationship(
        'RouteStop',
        primaryjoin='CurrentRouteStops.id==RouteStop.id',
        foreign_keys='(RouteStop.id)',
        uselist=False, viewonly=True, lazy='joined'
    )

    route_id = Column(String(255), index=True, nullable=False)
    route = relationship(
        'Route',
        primaryjoin='Route.route_id==CurrentRouteStops.route_id',
        foreign_keys='(Route.route_id)',
        uselist=False, viewonly=True, lazy='joined'
    )

    stop_id = Column(String(255), index=True, nullable=False)
    stop = relationship(
        'Stop',
        primaryjoin='Stop.stop_id==CurrentRouteStops.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=False, viewonly=True, lazy='joined'
    )

    order = Column(Integer, index=True, nullable=False)

    def __init__(self, route_stop):
        self.id = route_stop.id
        self.route_id = route_stop.route_id
        self.stop_id = route_stop.stop_id
        self.order = route_stop.order

    @classmethod
    def query_by_stop(cls, session, stop_id, agency_id=None, date=None, count=None, sort=False):
        """
        get all route stop records by looking for a given stop_id.
        further filtering can be had by providing an active date and agency id
        """
        # step 1: query stop id
        q = session.query(CurrentRouteStops).filter(CurrentRouteStops.stop_id == stop_id)
        if agency_id is not None:
            pass
            # TODO ... agency_id not in RouteStop -- should this even be here?
            # q = q.filter(RouteStop.agency_id == agency_id)

        # step 2: sort the results based on order column
        if sort:
            q = q.order_by(CurrentRouteStops.order)

        # step 3: limit the number of objects returned by query
        if count:
            q = q.limit(count)

        ret_val = q.all()
        return ret_val

    @classmethod
    def post_process(cls, db, **kwargs):
        """
        will update the current 'view' of this data
        """
        session = db.session()
        try:
            session.query(CurrentRouteStops).delete()

            rs_list = session.query(RouteStop).all()
            for rs in rs_list:
                if rs.is_active():
                    c = CurrentRouteStops(rs)
                    session.add(c)

            session.commit()
            session.flush()
        except Exception as e:
            log.warning(e)
            session.rollback()
        finally:
            session.flush()
            session.close()


__all__ = [RouteStop.__name__, CurrentRouteStops.__name__]
