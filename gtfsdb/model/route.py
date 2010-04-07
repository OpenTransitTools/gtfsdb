from gtfsdb.model import DeclarativeBase
from geoalchemy import GeometryColumn, GeometryDDL, MultiLineString
from sqlalchemy import Column, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func


__all__ = ['RouteType', 'Route']


class RouteType(DeclarativeBase):
    __tablename__ = 'route_type'
    
    route_type = Column(Integer, primary_key=True)
    route_type_name = Column(String)
    route_type_desc = Column(String)


class Route(DeclarativeBase):
    __tablename__ = 'routes'
    
    required_fields = [
        'route_id',
        'route_short_name',
        'route_long_name',
        'route_type'
    ]
    optional_fields = [
        'agency_id',
        'route_desc',
        'route_url',
        'route_color',
        'route_text_color'
    ]

    route_id = Column(String, primary_key=True)
    agency_id = Column(String)
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_desc = Column(String)
    route_type = Column(
        Integer,
        ForeignKey(RouteType.route_type),
        nullable=False
    )
    route_url = Column(String)
    route_color = Column(String(6))
    route_text_color = Column(String(6))

    def load_geometry(self, session):
        from gtfsdb.model.shape import Pattern
        from gtfsdb.model.trip import Trip
        if hasattr(self, 'geom'):
            s = func.st_simplify(Pattern.geom, 0.1)
            s = func.st_union(s)
            s = func.multi(s)
            s = func.astext(s).label('geom')
            q = session.query(s)
            q = q.filter(Pattern.trips.any((Trip.route == self)))
            self.geom = q.first().geom

    @classmethod
    def add_geometry_column(cls):
        cls.geom = GeometryColumn(MultiLineString(2))
        GeometryDDL(cls.__table__)

Index('%s_ix1' %(Route.__tablename__), Route.agency_id)
Index('%s_ix2' %(Route.__tablename__), Route.route_type)
