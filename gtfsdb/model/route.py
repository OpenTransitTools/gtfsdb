from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import func

from gtfsdb import config
from gtfsdb.model.base import Base


__all__ = ['RouteType', 'Route']


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
    agency_id = Column(
        String, ForeignKey('agency.agency_id'), index=True, nullable=True)
    route_short_name = Column(String(255))
    route_long_name = Column(String(255))
    route_desc = Column(String(255))
    route_type = Column(Integer, index=True, nullable=False)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))

    patterns = relationship('Pattern', secondary='trips')
    stop_times = relationship('StopTime', secondary='trips')
    trips = relationship('Trip')

    @classmethod
    def load_geoms(cls, db):
        from gtfsdb.model.shape import Pattern
        from gtfsdb.model.trip import Trip

        '''load derived geometries, currently only written for PostgreSQL'''
        if db.is_geospatial and db.is_postgresql:
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
            session.close()

    @classmethod
    def add_geometry_column(cls):
        from geoalchemy import GeometryColumn, GeometryDDL, MultiLineString

        cls.geom = GeometryColumn(MultiLineString(2))
        GeometryDDL(cls.__table__)
