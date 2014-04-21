import logging
import time

from sqlalchemy import Column
from sqlalchemy.orm import object_session, relationship
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import func

from gtfsdb import config
from gtfsdb.model.base import Base


__all__ = ['RouteType', 'Route', 'RouteDirection']


log = logging.getLogger(__name__)


class RouteType(Base):
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_type.txt'
    __tablename__ = 'route_type'

    route_type = Column(Integer, primary_key=True, autoincrement=False)
    route_type_name = Column(String(255))
    route_type_desc = Column(String(255))


class Route(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'routes.txt'

    __tablename__ = 'routes'

    route_id = Column(String(255), primary_key=True, nullable=False)
    agency_id = Column(String(255), index=True, nullable=True)
    route_short_name = Column(String(255))
    route_long_name = Column(String(255))
    route_desc = Column(String(255))
    route_type = Column(Integer, index=True, nullable=False)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    route_sort_order = Column(Integer, index=True)

    trips = relationship('Trip',
        primaryjoin='Route.route_id==Trip.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True)

    directions = relationship('RouteDirection',
        primaryjoin='Route.route_id==RouteDirection.route_id',
        foreign_keys='(Route.route_id)',
        uselist=True, viewonly=True)


    @property
    def route_name(self, fmt="{self.route_short_name}-{self.route_long_name}"):
        ''' build a route name out of long and short names...
        '''
        try:
            self._route_name
        except AttributeError:
            ret_val = self.route_long_name
            if self.route_long_name and self.route_short_name:
                ret_val = fmt.format(self=self)
            elif self.route_long_name is None:
                ret_val = self.route_short_name
            self._route_name = ret_val
        return self._route_name

    @property
    def _get_start_end_dates(self):
        '''find the min & max date using Trip & UniversalCalendar'''
        from gtfsdb.model.calendar import UniversalCalendar

        try:
            self._start_date
        except AttributeError:
            session = object_session(self)
            q = session.query(func.min(UniversalCalendar.date),
                              func.max(UniversalCalendar.date))
            q = q.filter(UniversalCalendar.trips.any(route_id=self.route_id))
            self._start_date, self._end_date = q.one()
        return self._start_date, self._end_date

    @property
    def start_date(self):
        return self._get_start_end_dates[0]

    @property
    def end_date(self):
        return self._get_start_end_dates[1]

    @classmethod
    def load_geoms(cls, db):
        '''load derived geometries, currently only written for PostgreSQL'''
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
        from geoalchemy import GeometryColumn, GeometryDDL, MultiLineString

        cls.geom = GeometryColumn(MultiLineString(2))
        GeometryDDL(cls.__table__)


class RouteDirection(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'route_directions.txt'

    __tablename__ = 'route_directions'

    route_id = Column(String(255), primary_key=True, nullable=False)
    direction_id = Column(Integer, primary_key=True, nullable=False)
    direction_name = Column(String(255))
