import sys
import time
import datetime
import logging
log = logging.getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.types import Integer, String, Date

from gtfsdb import config
from gtfsdb.model.base import Base

__all__ = ['RouteStop']


class RouteStop(Base):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'route_stops'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    direction_id = Column(Integer, primary_key=True, index=True, nullable=False)
    stop_id = Column(String(255), primary_key=True, index=True, nullable=False)
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
        """ :return False whenever we see that the route_stop's start and end date are
                    outside the input date (where the input date defaults to 'today')
        """
        _is_active = False
        if self.start_date and self.end_date:
            if date is None:
                date = datetime.date.today()
            if self.start_date <= date <= self.end_date:
                _is_active = True
        return _is_active

    @classmethod
    def active_stops(cls, session, route_id, direction_id, agency_id=None, date=None):
        ''' returns list of routes that are seen as 'active' based on dates and filters
        '''

        # step 1: default date
        if date is None or not isinstance(date, datetime.date):
            date = datetime.date.today()

        # step 2a: query all route stops
        q = session.query(RouteStop).filter(RouteStop.route_id == route_id).filter(RouteStop.direction_id == direction_id)

        # step 2b: filter based on date
        q = q.filter(RouteStop.start_date <= date).filter(date <= RouteStop.end_date)

        # step 2c: filter by any agency_id
        if agency_id:
            q = q.filter(RouteStop.agency_id == agency_id)

        # step 2d: add some stop order
        q = q.order_by(RouteStop.order)

        #import pdb; pdb.set_trace()
        route_stops = q.all()
        return route_stops

    @classmethod
    def load(cls, db, **kwargs):
        log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))
        pass

    @classmethod
    def post_process(cls, db):
        log.debug('{0}.post_process'.format(cls.__name__))
        cls.populate(db.session)

    @classmethod
    def populate(cls, session):
        ''' for each route/direction, find list of stop_ids for route/direction pairs

            the load is a two part process, where part A finds a list of unique stop ids, and
            part B creates the RouteStop (and potentially RouteDirections ... if not in GTFS) records
        '''
        from gtfsdb import Route, RouteDirection

        #import pdb; pdb.set_trace()
        start_time = time.time()
        routes = session.query(Route).all()

        # step 0: for each route...
        for r in routes:

            # step 1: filter the list of trips down to only a trip with a unique pattern
            #   TODO: any way to have the orm do this?  Something probably really simple Mike?
            trips = []
            shape_id_filter = []
            for t in r.trips:
                if t.shape_id not in shape_id_filter:
                    shape_id_filter.append(t.shape_id)
                    trips.append(t)

            # step 2: sort our list of trips by length (note: for trips with two directions, ...)
            trips = sorted(trips, key=lambda t: t.trip_len, reverse=True)

            # PART A: we're going to just collect a list of unique stop ids for this route / directions 
            for d in [0, 1]:
                unique_stops_ids = []

                # step 3: loop through all our trips and their stop times, pulling out a unique set of stops 
                for t in trips:
                    if t.direction_id == d:

                        # step 4: loop through this trip's stop times, and find any/all stops that are in our stop list already
                        #         further, let's try to find the best position of that stop (e.g., look for where the stop patterns breaks)
                        last_pos = None
                        for i, st in enumerate(t.stop_times):
                            # step 5a: make sure this stop that customers can actually board...
                            if st.is_boarding_stop():
                                if st.stop_id in unique_stops_ids:
                                    last_pos = unique_stops_ids.index(st.stop_id)
                                else:
                                    # step 5b: add ths stop id to our unique list ... either in position, or appended to the end of the list
                                    if last_pos:
                                        last_pos += 1
                                        unique_stops_ids.insert(last_pos, st.stop_id)
                                    else:
                                        unique_stops_ids.append(st.stop_id)

                # PART B: add records to the database ...
                if len(unique_stops_ids) > 0:

                    # step 6: if a RouteDirection doesn't exist, let's create it...
                    if r.directions is None or len(r.directions) == 0:
                        rd = RouteDirection()
                        rd.route_id = r.route_id
                        rd.direction_id = d
                        rd.direction_name = "Outbound" if d is 0 else "Inbound"
                        session.add(rd)

                    # step 7: create new RouteStop records
                    for k, stop_id in enumerate(unique_stops_ids):
                        # step 4b: create a RouteStop record
                        rs = RouteStop()
                        rs.route_id = r.route_id
                        rs.direction_id = d
                        rs.stop_id = stop_id
                        rs.order = k + 1
                        s, e = cls._calculate_times(r, stop_id)
                        rs.start_date = s
                        rs.end_date =  e
                        session.add(rs)

                    # step 8: flush the new records to the db...
                    sys.stdout.write('*')
                    session.commit()
                    session.flush()
                    unique_stops_ids = [None]

        session.commit()
        session.close()

        processing_time = time.time() - start_time
        log.debug('{0}.post_process ({1:.0f} seconds)'.format(cls.__name__, processing_time))

    @classmethod
    def _calculate_times(cls, r, stop_id):
        s = r.start_date
        e = r.end_date
        return s, e