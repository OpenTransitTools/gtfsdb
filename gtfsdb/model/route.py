import datetime
import time
import logging
log = logging.getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import func

from gtfsdb import config
from gtfsdb.model.base import Base

__all__ = ['RouteType', 'Route', 'RouteDirection', 'RouteFilter']


class RouteType(Base):
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_type.txt'
    __tablename__ = 'route_type'

    route_type = Column(Integer, primary_key=True, index=True, autoincrement=False)
    route_type_name = Column(String(255))
    route_type_desc = Column(String(1023))


class Route(Base):
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
    min_headway_minutes = Column(Integer) # Trillium extension.

    trips = relationship(
        'Trip',
        primaryjoin='Route.route_id==Trip.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True)

    directions = relationship(
        'RouteDirection',
        primaryjoin='Route.route_id==RouteDirection.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True, lazy='joined')

    @property
    def route_name(self, fmt="{self.route_short_name}-{self.route_long_name}"):
        """ build a route name out of long and short names...
        """
        if not self.is_cached_data_valid('_route_name'):
            log.warn("query route name")
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
            dir = self.directions.filter(RouteDirection.direction_id==direction_id)
            if dir and dir.direction_name:
                ret_val = dir.direction_name
        except:
            pass
        return ret_val

    def is_active(self, date=None):
        """ :return False whenever we see that the route start and end date are outside the
                    input date (where the input date defaults to 'today')
        """
        _is_active = True
        if self.start_date and self.end_date:
            _is_active = False
            if date is None:
                date = datetime.date.today()
            if self.start_date <= date <= self.end_date:
                _is_active = True
        return _is_active

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

    @property
    def start_date(self):
        return self._get_start_end_dates[0]

    @property
    def end_date(self):
        return self._get_start_end_dates[1]

    @classmethod
    def load_geoms(cls, db):
        """load derived geometries, currently only written for PostgreSQL"""
        from gtfsdb.model.shape import Pattern
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
            log.debug('{0}.load_geoms ({1:.0f} seconds)'.format(
                cls.__name__, processing_time))

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            cls.geom = deferred(Column(Geometry('MULTILINESTRING')))

    @classmethod
    def active_routes(cls, session, date=None):
        """ returns list of routes that are seen as 'active' based on dates and filters
        """
        ret_val = []

        # step 1: grab all stops
        routes = session.query(Route).filter(~Route.route_id.in_(session.query(RouteFilter.route_id))).order_by(Route.route_sort_order).all()

        # step 2: default date
        if date is None or not isinstance(date, datetime.date):
            date = datetime.date.today()

        # step 3: filter routes by active date
        #         NOTE: r.start_date and r.end_date are properties, so have to do in code vs. query
        for r in routes:
            if r:
                # step 3a: filter based on date (if invalid looking date objects, just pass the route on)
                if r.start_date and r.end_date:
                    if r.start_date <= date <= r.end_date:
                        ret_val.append(r)
                else:
                    ret_val.append(r)
        return ret_val

    @classmethod
    def active_route_ids(cls, session):
        """ return an array of route_id / agency_id pairs
            {route_id:'2112', agency_id:'C-TRAN'}
        """
        ret_val = []
        routes = cls.active_routes(session)
        for r in routes:
            ret_val.append({"route_id":r.route_id, "agency_id":r.agency_id})
        return ret_val


class RouteDirection(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'route_directions.txt'

    __tablename__ = 'route_directions'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    direction_id = Column(Integer, primary_key=True, index=True, nullable=False)
    direction_name = Column(String(255))


class RouteFilter(Base):
    """ list of filters to be used to cull routes from certain lists
        e.g., there might be Shuttles that you never want to be shown...you can load that data here, and
        use it in your queries
    """
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_filter.txt'
    __tablename__ = 'route_filters'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    agency_id = Column(String(255), index=True, nullable=True)
    description = Column(String)
