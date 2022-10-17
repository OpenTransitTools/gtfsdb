from collections import defaultdict

from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import joinedload, object_session, relationship

from gtfsdb import config, util
from gtfsdb.model.base import Base
from .stop_base import StopBase

import logging
log = logging.getLogger(__name__)


class Stop(Base, StopBase):
    datasource = config.DATASOURCE_GTFS
    filename = 'stops.txt'

    __tablename__ = 'stops'

    stop_id = Column(String(255), primary_key=True, index=True, nullable=False)
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
    direction = Column(String(50))
    position = Column(String(50))

    stop_features = relationship(
        'StopFeature',
        primaryjoin='Stop.stop_id==StopFeature.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, viewonly=True)

    stop_times = relationship(
        'StopTime',
        primaryjoin='Stop.stop_id==StopTime.stop_id',
        foreign_keys='(Stop.stop_id)',
        uselist=True, viewonly=True)

    @classmethod
    def add_geom_to_dict(cls, row):
        point = util.Point.make_geo(row['stop_lon'], row['stop_lat'], config.SRID)
        row['geom'] = point

    @property
    def routes(self):
        """
        return list of routes servicing this stop
        @todo: rewrite the cache to use timeout checking in Base.py
        """
        try:
            self._routes
        except AttributeError:
            from gtfsdb.model.route import Route
            from gtfsdb.model.trip import Trip
            from gtfsdb.model.stop_time import StopTime
            session = object_session(self)
            q = session.query(Route)
            f = ((StopTime.stop_id == self.stop_id) & (StopTime.departure_time != ''))
            q = q.filter(Route.trips.any(Trip.stop_times.any(f)))
            q = q.order_by(Route.route_sort_order)
            self._routes = q.all()
        return self._routes

    @property
    def headsigns(self):
        """
        Returns a dictionary of all unique (route_id, headsign) tuples used
        at the stop and the number of trips the head sign is used
        """
        if not hasattr(self, '_headsigns'):
            from gtfsdb.model.stop_time import StopTime
            self._headsigns = defaultdict(int)
            session = object_session(self)
            log.info("QUERY StopTime")
            q = session.query(StopTime)
            q = q.options(joinedload('trip').joinedload('route'))
            q = q.filter_by(stop_id=self.stop_id)
            for r in q:
                headsign = r.stop_headsign or r.trip.trip_headsign
                self._headsigns[(r.trip.route, headsign)] += 1
        return self._headsigns

    @property
    def agencies(self):
        """
        return list of agency ids with routes hitting this stop
        @todo: rewrite the cache to use timeout checking in Base.py
        """
        try:
            self._agencies
        except AttributeError:
            self._agencies = []
            if self.routes:
                for r in self.routes:
                    if r.agency_id not in self._agencies:
                        self.agencies.append(r.agency_id)
        return self._agencies

    @property
    def amenities(self):
        """
        return list of strings for the stop amenity (feature) names
        """
        try:
            self._amenities
        except AttributeError:
            self._amenities = []
            if self.stop_features and len(self.stop_features) > 0:
                for f in self.stop_features:
                    n = f.feature_name
                    if n and len(n) > 0:
                        self._amenities.append(n)
                self._amenities = sorted(self._amenities)
        return self._amenities

    def is_active(self, date=None):
        """
        :return False whenever we see that the stop has zero stop_times on the given input date
                (which defaults to 'today')

        @NOTE: use caution with this routine.  calling this for multiple stops can really slow things down,
               since you're querying large trip and stop_time tables, and asking for a schedule of each stop
               I used to call this multiple times via route_stop to make sure each stop was active ... that
               was really bad performance wise.
        """
        from gtfsdb.model.stop_time import StopTime

        # import pdb; pdb.set_trace()
        _is_active = False
        date = util.check_date(date)
        st = StopTime.get_departure_schedule(self.session, self.stop_id, date, limit=1)
        if st and len(st) > 0:
            _is_active = True
        return _is_active

    @classmethod
    def query_active_stops(cls, session, limit=None, location_types=[0], active_filter=True, date=None):
        """
        check for active stops
        """
        # step 1: get stops
        q = session.query(Stop)
        if limit:
            q = q.limit(limit)
        if location_types and len(location_types) > 0:
            # note: default is to filter location_type=0, which is just stops (not stations)
            q.filter(Stop.location_type.in_(location_types))
        stops = q.all()

        # step 2: filter active stops only ???
        if active_filter:
            ret_val = []
            for s in stops:
                if s.is_active(date):
                    ret_val.append(s)
        else:
            ret_val = stops
        return ret_val

    @classmethod
    def query_active_stop_ids(cls, session, limit=None, active_filter=True):
        """
        return an array of stop_id / agencies pairs
        {stop_id:'2112', agencies:['C-TRAN', 'TRIMET']}
        """
        ret_val = []
        stops = cls.query_active_stops(session, limit, active_filter)
        for s in stops:
            ret_val.append({"stop_id": s.stop_id, "agencies": s.agencies})
        return ret_val


class CurrentStops(Base, StopBase):
    """
    this table is (optionally) used as a view into the currently active routes
    it is pre-calculated to list routes that are currently running service
    (GTFS can have multiple instances of the same route, with different aspects like name and direction)
    """
    datasource = config.DATASOURCE_DERIVED
    __tablename__ = 'current_stops'

    route_short_names = Column(String(1023))
    route_type = Column(Integer)
    route_type_other = Column(Integer)
    route_mode = Column(String(255))

    stop_id = Column(String(255), primary_key=True, index=True, nullable=False)
    location_type = Column(Integer)
    stop_lat = Column(Numeric(12, 9), nullable=False)
    stop_lon = Column(Numeric(12, 9), nullable=False)

    stop = relationship(
        Stop.__name__,
        primaryjoin='CurrentStops.stop_id==Stop.stop_id',
        foreign_keys='(CurrentStops.stop_id)',
        uselist=False, viewonly=True,
        lazy="joined", innerjoin=True,
    )

    def __init__(self, stop, session):
        """
        create a CurrentStop record from a stop record
        :param stop:
        :param session:
        """
        self.stop_id = stop.stop_id
        self.location_type = stop.location_type
        self.stop_lon = stop.stop_lon
        self.stop_lat = stop.stop_lat

        # copy the stop geom to CurrentStops (if we're in is_geospatial mode)
        if hasattr(stop, 'geom') and hasattr(self, 'geom'):
            self.geom = util.Point.make_geo(stop.stop_lon, stop.stop_lat, config.SRID)

        # convoluted route type assignment ... handle conditon where multiple modes (limited to 2) serve same stop
        # import pdb; pdb.set_trace()
        from .route_stop import CurrentRouteStops
        rs_list = CurrentRouteStops.query_route_short_names(session, stop, filter_active=True)
        for rs in rs_list:
            type = rs.get('type')
            if self.route_mode is None:
                self.route_type = type.route_type
                self.route_mode = type.otp_type
            elif type.is_different_mode(self.route_type):
                if type.is_lower_priority(self.route_type):
                    self.route_type_other = self.route_type
                    self.route_type = type.route_type
                    self.route_mode = type.otp_type
                else:
                    self.route_type_other = type.route_type

        # route short names
        self.route_short_names = CurrentRouteStops.to_route_short_names_as_string(rs_list)

    @classmethod
    def post_process(cls, db, **kwargs):
        """
        will update the current 'view' of this data
        """
        session = db.session()
        try:
            session.query(CurrentStops).delete()

            # import pdb; pdb.set_trace()
            for s in Stop.query_active_stops(session):
                c = CurrentStops(s, session)
                session.add(c)

            session.commit()
            session.flush()
        except Exception as e:
            log.warning(e)
            session.rollback()
        finally:
            session.flush()
            session.close()


__all__ = [Stop.__name__, CurrentStops.__name__]
