import time

from gtfsdb import config, util
from gtfsdb.model.base import Base
from .route_base import RouteBase

from sqlalchemy import Column
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Integer, String

import logging
log = logging.getLogger(__name__)


class Route(Base, RouteBase):
    datasource = config.DATASOURCE_GTFS
    filename = 'routes.txt'

    __tablename__ = 'routes'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    agency_id = Column(String(255), index=True, nullable=True)
    route_short_name = Column(String(255))
    route_long_name = Column(String(255))
    route_desc = Column(String(1023))
    route_type = Column(Integer, index=True, nullable=False)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    route_sort_order = Column(Integer, index=True)
    min_headway_minutes = Column(Integer)  # Trillium extension.

    agency = relationship(
        'Agency',
        primaryjoin='Route.agency_id==Agency.agency_id',
        foreign_keys='(Route.agency_id)',
        uselist=False, viewonly=True,
        lazy="joined", # don't innerjoin ... causes unit test errors
    )

    type = relationship(
        'RouteType',
        primaryjoin='Route.route_type==RouteType.route_type',
        foreign_keys='(Route.route_type)',
        uselist=False, viewonly=True,
        lazy="joined", innerjoin=True,
    )

    trips = relationship(
        'Trip',
        primaryjoin='Route.route_id==Trip.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True
    )

    directions = relationship(
        'RouteDirection',
        primaryjoin='Route.route_id==RouteDirection.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True
    )

    def is_active(self, date=None):
        """
        :return False whenever we see that the route start and end date are outside the
                input date (where the input date defaults to 'today')
        """
        _is_active = True
        if self.start_date or self.end_date:
            _is_active = False
            date = util.check_date(date)
            if self.start_date and self.end_date:  # keep this as nested if (don't combine due to below)
                if self.start_date <= date <= self.end_date:
                    _is_active = True
            elif self.start_date and self.start_date <= date:
                _is_active = True
            elif self.end_date and date <= self.end_date:
                _is_active = True
        return _is_active

    @property
    def route_name(self, fmt="{self.route_short_name}-{self.route_long_name}"):
        """
        build a route name out of long and short names...
        """
        if not self.is_cached_data_valid('_route_name'):
            log.warning("query route name")
            ret_val = self.route_long_name
            if self.route_long_name and self.route_short_name:
                ret_val = fmt.format(self=self)
            elif self.route_long_name is None:
                ret_val = self.route_short_name
            self._route_name = ret_val
            self.update_cached_data('_route_name')

        return self._route_name

    def direction_name(self, direction_id, def_val=''):
        ret_val = def_val
        try:
            dir = self.directions.filter(RouteDirection.direction_id == direction_id)
            if dir and dir.direction_name:
                ret_val = dir.direction_name
        except Exception as e:
            log.debug(e)
            pass
        return ret_val

    @property
    def start_date(self):
        return self._get_start_end_dates[0]

    @property
    def end_date(self):
        return self._get_start_end_dates[1]

    @property
    def _get_start_end_dates(self):
        """find the min & max date using Trip & UniversalCalendar"""
        if not self.is_cached_data_valid('_start_date'):
            from gtfsdb.model.calendar import UniversalCalendar
            q = self.session.query(func.min(UniversalCalendar.date), func.max(UniversalCalendar.date))
            q = q.filter(UniversalCalendar.trips.any(route_id=self.route_id))
            self._start_date, self._end_date = q.one()
            self.update_cached_data('_start_date')

        return self._start_date, self._end_date

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            cls.geom = deferred(Column(Geometry('MULTILINESTRING')))

    @classmethod
    def load_geoms(cls, db):
        """ load derived geometries, currently only written for PostgreSQL """
        from gtfsdb.model.pattern import Pattern
        from gtfsdb.model.trip import Trip

        if db.is_geospatial and db.is_postgresql:
            start_time = time.time()
            session = db.session
            routes = session.query(Route).all()
            for route in routes:
                s = func.st_collect(Pattern.geom)
                s = func.st_multi(s)
                s = func.st_astext(s).label('geom')
                q = session.query(s)
                q = q.filter(Pattern.trips.any((Trip.route == route)))
                route.geom = q.first().geom
                session.merge(route)
            session.commit()
            processing_time = time.time() - start_time
            log.debug('{0}.load_geoms ({1:.0f} seconds)'.format(cls.__name__, processing_time))

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))
        cls.load_geoms(db)


class CurrentRoutes(Base, RouteBase):
    """
    this table is (optionally) used as a view into the currently active routes
    it is pre-calculated to list routes that are currently running service
    (GTFS can have multiple instances of the same route, with different aspects like name and direction)
    """
    datasource = config.DATASOURCE_DERIVED
    __tablename__ = 'current_routes'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    route = relationship(
        Route.__name__,
        primaryjoin='CurrentRoutes.route_id==Route.route_id',
        foreign_keys='(CurrentRoutes.route_id)',
        uselist=False, viewonly=True,
        lazy="joined", innerjoin=True,
    )

    route_sort_order = Column(Integer)

    def __init__(self, route, def_order):
        self.route_id = route.route_id
        self.route_sort_order = route.route_sort_order if route.route_sort_order else def_order

    def is_active(self, date=None):
        ret_val = True
        if date:
            log.warning("you're calling CurrentRoutes.is_active with a date, which is both slow and redundant...")
            ret_val = self.route.is_active(date)
        return ret_val

    @classmethod
    def query_route(cls, session, route_id, detailed=False):
        """ get a gtfsdb Route object from the db """
        r = super(CurrentRoutes, cls).query_route(session, route_id, detailed)
        return r.route

    @classmethod
    def query_active_routes(cls, session, date=None):
        """
        wrap base active route query
        :return list of Route orm objects
        """
        ret_val = []
        if date:
            log.warning("you're calling CurrentRoutes.active_routes with a date, which is slow...")
            ret_val = Route.query_active_routes(session, date)
        else:
            try:
                clist = session.query(CurrentRoutes).order_by(CurrentRoutes.route_sort_order).all()
                for r in clist:
                    ret_val.append(r.route)
            except Exception as e:
                log.warning(e)
        return ret_val

    @classmethod
    def post_process(cls, db, **kwargs):
        """
        will update the current 'view' of this data

        steps:
          1. open transaction
          2. drop all data in this 'current' table
          3. select current routes as a list
          4. add those id's to this table
          5. other processing (cached results)
          6. commit
          7. close transaction
        """
        session = db.session()
        num_inserts = 0
        try:
            session.query(CurrentRoutes).delete()

            # import pdb; pdb.set_trace()
            rte_list = Route.query_active_routes(session)
            for i, r in enumerate(rte_list):
                c = CurrentRoutes(r, i+1)
                session.add(c)
                num_inserts += 1

            session.commit()
            session.flush()
        except Exception as e:
            log.warning(e)
            session.rollback()
        finally:
            session.flush()
            session.close()
        if num_inserts == 0:
            log.warning("CurrentRoutes did not insert any route records...hmmmm...")


class RouteDirection(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'route_directions.txt'

    __tablename__ = 'route_directions'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    direction_id = Column(Integer, primary_key=True, index=True, nullable=False)
    direction_name = Column(String(255))


class RouteType(Base):
    """
    OTP TYPES (come via service calls)
    0:TRAM, 1:SUBWAY, 2:RAIL, 3:BUS, 4:FERRY, 5:CABLE_CAR, 6:GONDOLA, 7:FUNICULAR
    :see https://github.com/opentripplanner/OpenTripPlanner/blob/master/src/main/java/org/opentripplanner/routing/core/TraverseMode.java :
    """
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_type.txt'
    __tablename__ = 'route_type'

    route_type = Column(Integer, primary_key=True, index=True, autoincrement=False)
    otp_type = Column(String(255))
    route_type_name = Column(String(255))
    route_type_desc = Column(String(1023))

    def is_bus(self):
        return self.route_type == 3

    def is_different_mode(self, cmp_route_type):
         return self.route_type != cmp_route_type

    def is_higher_priority(self, cmp_route_type):
        """ abitrary compare of route types, where lower numbrer means higher priority in terms mode ranking (sans bus) """
        ret_val = False
        if cmp_route_type != 3 and cmp_route_type < self.route_type:
            ret_val = True
        return ret_val

    def is_lower_priority(self, cmp_route_type):
        """ abitrary compare of route types, where lower numbrer means higher priority in terms mode ranking (sans bus) """
        ret_val = False
        if cmp_route_type != self.route_type:
            if cmp_route_type == 3 or cmp_route_type > self.route_type:
                ret_val = True
        return ret_val


class RouteFilter(Base):
    """
    list of filters to be used to cull routes from certain lists
    e.g., there might be Shuttles that you never want to be shown...you can load that data here, and
    use it in your queries
    """
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_filter.txt'
    __tablename__ = 'route_filters'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    agency_id = Column(String(255), index=True, nullable=True)
    description = Column(String(1023))


__all__ = [RouteType.__name__, Route.__name__, RouteDirection.__name__, RouteFilter.__name__, CurrentRoutes.__name__]