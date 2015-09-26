import logging
import datetime
from collections import defaultdict

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String, Index
from sqlalchemy.orm import joinedload_all, object_session, relationship

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID


log = logging.getLogger(__name__)

class Stop(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stops.txt'

    __tablename__ = 'gtfs_stops'

    stop_id = Column(GUID(), primary_key=True, nullable=False)
    stop_code = Column(String(50))
    stop_name = Column(String(255), nullable=False)
    stop_desc = Column(String(255))
    stop_lat = Column(Numeric(12, 9), nullable=False)
    stop_lon = Column(Numeric(12, 9), nullable=False)
    zone_id = Column(GUID())
    stop_url = Column(String(255))
    location_type = Column(Integer, default=0)
    parent_station = Column(String(255))
    stop_timezone = Column(String(50))
    wheelchair_boarding = Column(Integer, default=0)
    platform_code = Column(String(50))
    direction = Column(String(50))
    position = Column(String(50))
    the_geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    stop_times = relationship('StopTime', primaryjoin="Stop.stop_id==StopTime.stop_id",
                              foreign_keys='(StopTime.stop_id)', uselist=True)

    stop_features = relationship(
        'StopFeature',
        primaryjoin='Stop.stop_id==StopFeature.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, cascade='delete')

    transfers_out = relationship('Transfer', primaryjoin="Stop.stop_id==Transfer.from_stop_id",
                                 foreign_keys='(Transfer.from_stop_id)', uselist=True, cascade='delete')
    transfers_in = relationship('Transfer', primaryjoin="Stop.stop_id==Transfer.to_stop_id",
                                 foreign_keys='(Transfer.to_stop_id)', uselist=True, cascade='delete')


    @property
    def is_active(self, date=None):
        return True

    @property
    def is_active(self, date=None):
        """ :return False whenever we see that the stop has zero stop_times on the given
                    input date (which defaults to 'today')
        """
        ret_val = False
        if date is None:
            date = datetime.date.today()

        #import pdb; pdb.set_trace()
        from gtfsdb.model.stop_time import StopTime
        st = StopTime.get_departure_schedule(self.session, self.stop_id, date, limit=1)
        if st and len(st) > 0:
            ret_val = True
        return ret_val

    @classmethod
    def add_geometry_column(cls):
        #todo remove
        pass

    @classmethod
    def add_geom_to_dict(cls, row):
        args = (config.SRID, row['stop_lon'], row['stop_lat'])
        row['the_geom'] = 'SRID={0};POINT({1} {2})'.format(*args)


    """ TODO: rewrite the cache to use timeout checking in Base.py """

    @property
    def headsigns(self):
        '''Returns a dictionary of all unique (route_id, headsign) tuples used
        at the stop and the number of trips the head sign is used'''
        if not hasattr(self, '_headsigns'):
            from gtfsdb.model.stop_time import StopTime
            self._headsigns = defaultdict(int)
            session = object_session(self)
            log.info("QUERY StopTime")
            q = session.query(StopTime)
            q = q.options(joinedload_all('trip.route'))
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
        from gtfsdb.model.stop_time import StopTime

        try:
            self._routes
        except AttributeError:
            session = object_session(self)
            q = session.query(Route)
            f = ((StopTime.stop_id == self.stop_id) & (StopTime.departure_time != ''))
            q = q.filter(Route.trips.any(Trip.stop_times.any(f)))
            q = q.order_by(Route.route_sort_order)
            self._routes = q.all()
        return self._routes

Index('ix_gtfs_stops_stop_id', Stop.stop_id, postgresql_using='hash')
