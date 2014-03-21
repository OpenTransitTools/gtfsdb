from collections import defaultdict

from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import joinedload, object_session, relationship

from gtfsdb import config
from gtfsdb.model.base import Base


class Stop(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stops.txt'

    __tablename__ = 'stops'

    stop_id = Column(String(255), primary_key=True, nullable=False)
    stop_code = Column(String(50))
    stop_name = Column(String(255), nullable=False)
    stop_desc = Column(String(255))
    stop_lat = Column(Numeric(12, 9), nullable=False)
    stop_lon = Column(Numeric(12, 9), nullable=False)
    zone_id = Column(String(50))
    stop_url = Column(String(255))
    location_type = Column(Integer, index=True, default=0)
    parent_station = Column(String(255))
    stop_timezone = Column(String(50))
    wheelchair_boarding = Column(Integer, default=0)
    platform_code = Column(String(50))

    stop_features = relationship('StopFeature',
        primaryjoin='Stop.stop_id==StopFeature.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, viewonly=True)

    stop_times = relationship('StopTime',
        primaryjoin='Stop.stop_id==StopTime.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, viewonly=True)

    @property
    def headsigns(self):
        '''Returns a dictionary of all unique (route_id, headsign) tuples used
        at the stop and the number of trips the head sign is used'''
        from gtfsdb.model.stop_time import StopTime

        try:
            self._headsigns
        except AttributeError:
            self._headsigns = defaultdict(int)
            session = object_session(self)
            q = session.query(StopTime).options(joinedload('trip'))
            q = q.filter_by(stop_id=self.stop_id)
            for r in q:
                headsign = r.stop_headsign or r.trip.trip_headsign
                self._headsigns[(r.trip.route, headsign)] += 1
        return self._headsigns

    @property
    def routes(self):
        ''''''
        from gtfsdb.model.route import Route
        from gtfsdb.model.trip import Trip

        try:
            self._routes
        except AttributeError:
            session = object_session(self)
            q = session.query(Route)
            q = q.filter(Route.trips.any(
                Trip.stop_times.any(stop_id=self.stop_id)))
            self._routes = q.all()
        return self._routes

    @classmethod
    def add_geometry_column(cls):
        from geoalchemy import GeometryColumn, GeometryDDL, Point

        cls.geom = GeometryColumn(Point(2))
        GeometryDDL(cls.__table__)

    @classmethod
    def add_geom_to_dict(cls, row):
        try:
            from geoalchemy import WKTSpatialElement
            wkt = 'SRID=%s;POINT(%s %s)' % (
                config.SRID,
                row['stop_lon'],
                row['stop_lat']
            )
            row['geom'] = WKTSpatialElement(wkt)
        except ImportError:
            pass
