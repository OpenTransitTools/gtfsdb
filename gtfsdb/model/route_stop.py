import sys
import time
import logging
log = logging.getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.types import Integer, String

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

    @classmethod
    def load(cls, db, **kwargs):
        ''' for each route/direction, find list of stop_ids for route/direction pairs

            the load is a two part process, where part A finds a list of unique stop ids, and
            part B creates the RouteStop (and potentially RouteDirections ... if not in GTFS) records
        '''
        from gtfsdb import Route, RouteDirection

        start_time = time.time()
        session = db.session
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
                        session.add(rs)

                    # step 8: flush the new records to the db...
                    sys.stdout.write('*')
                    session.commit()
                    session.flush()
                    unique_stops_ids = [None]

        session.commit()
        session.close()

        processing_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(cls.__name__, processing_time))

