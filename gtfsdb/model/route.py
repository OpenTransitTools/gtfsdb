import time

from gtfsdb import config, util
from gtfsdb.model.base import Base
from .route_base import RouteBase

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Integer, String, Boolean

import logging
log = logging.getLogger(__name__)


"""
TODO: 
service_type = LRT (MAX), HRT (WES), BUS, OWL?, SC, AT, CC (Community Circ.) etc...
service_type = Column(String(7)) 
 - add service_type enum w/another table
 - add a scheme to customize things based on agency
 - so customize/trimet.py and customize/ctran.py, etc...
 - this would do route_type=1 + route_id=100/192 = service_type MAX, etc... per agency
 - would also customize the route_label formatting per agency
 - https://www.itsmarta.com/uploadedFiles/MARTA_101/Why_MARTA/ServiceTypesMatrix.pdf
 - etc...
"""

class Route(Base, RouteBase):
    datasource = config.DATASOURCE_GTFS
    filename = 'routes.txt'

    __tablename__ = 'routes'

    route_id = Column(String(255), primary_key=True, index=True, nullable=False)
    agency_id = Column(String(255), index=True, nullable=True)
    route_short_name = Column(String(255))
    route_long_name = Column(String(255))
    route_label = Column(String(511))
    route_desc = Column(String(1023))
    route_type = Column(Integer, index=True, nullable=False)
    service_type = Column(String(7))  # TODO: enum LRT, HRT, BUS, SC, AT, 
    route_url = Column(String(255))
    route_color = Column(String(7), default=config.default_route_color)
    route_alt_color = Column(String(7), default=config.default_route_color)
    route_text_color = Column(String(7), default=config.default_text_color)
    route_sort_order = Column(Integer, index=True)
    min_headway_minutes = Column(Integer)  # Trillium extension.
    is_frequent = Column(Boolean, default=False)

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
            log.info("query route name")
            ret_val = self.route_long_name
            if self.route_long_name and self.route_short_name and self.route_long_name != self.route_short_name:
                ret_val = fmt.format(self=self)
            elif self.route_long_name is None:
                ret_val = self.route_short_name
            self._route_name = ret_val
            self.update_cached_data('_route_name')

        # add the route_name to db's route_label column so it's available by non-ORM clients (GeoServer)
        if self.route_label is None:
            self.route_label = self._route_name

        return self._route_name

    def direction_name(self, direction_id, def_val=''):
        ret_val = def_val
        try:
            dir = self.directions.filter(RouteDirection.direction_id == direction_id)
            if dir and dir.direction_name:
                ret_val = dir.direction_name
        except Exception as e:
            log.error(e)
        return ret_val

    @property
    def start_date(self):
        return self._get_start_end_dates[0]

    @property
    def end_date(self):
        return self._get_start_end_dates[1]

    def _calc_frequency(self):
        # TODO: do better here...
        self.is_frequent = len(self.trips) > 50

    def _fix_colors(self):
        # step 0: default colors
        if not util.is_string(self.route_color): self.route_color = config.default_route_color
        if not util.is_string(self.route_text_color): self.route_text_color = config.default_text_color

        # step 1: fix (add) a '#' to the route color
        if self.route_color[0] != '#':
            self.route_color = '#' + self.route_color
        if self.route_text_color[0] != '#':
            self.route_text_color = '#' + self.route_text_color

        # step 2: figure out the alt colors
        self.route_alt_color = self.route_color
        if not self.is_bus or self.is_brt or self.is_frequent:
            if self.route_color == config.default_route_color:
                self.route_color = config.default_frequent_color
                self.route_alt_color = config.default_frequent_color

        #print(self.agency_id, self.route_id, self.route_color)

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
    def post_process(cls, db, **kwargs):
        # import pdb; pdb.set_trace()
        log.debug('{0}.post_process'.format(cls.__name__))
        start_time = time.time()
        session = db.session

        route_list = session.query(Route).all()
        cls._load_geoms(db, route_list)
        for route in route_list:
            route.route_name  # populate route_label column
            route._calc_frequency()
            route._fix_colors()
            session.merge(route)
        session.commit()
        session.flush()
        processing_time = time.time() - start_time
        log.debug('{0}.load_geoms ({1:.0f} seconds)'.format(cls.__name__, processing_time))


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
        SORT_ORDER_OFFSET = 1000001

        num_inserts = 0        
        try:
            session.query(CurrentRoutes).delete()

            # filter by date, or copy all
            # import pdb; pdb.set_trace()
            date = util.check_date(kwargs.get('date'))
            filter = True
            if kwargs.get('current_tables_all'):
                date = None
                filter = False

            cr_list = []
            rte_list = Route.query_active_routes(session, date, filter)
            for i, r in enumerate(rte_list):
                c = CurrentRoutes(r, SORT_ORDER_OFFSET + i)
                cr_list.append(c)
                session.add(c)
                num_inserts += 1
            
            #import pdb; pdb.set_trace()
            cls._load_geoms(db, cr_list, date)

            session.commit()
            session.flush()
        except Exception as e:
            log.error(e)
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
