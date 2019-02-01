try:
    import unittest2 as unittest
except ImportError:
    import unittest

from .base import *
from gtfsdb import *
from gtfsdb import util


import logging
log = logging.getLogger(__name__)


class TestCurrent(unittest.TestCase):
    db = None
    DO_PG = False
    PG_URL = "postgresql://ott@localhost:5432/ott"
    PG_SCHEMA = "current_test"

    def setUp(self):
        if TestCurrent.db is None:
            TestCurrent.db = load_pgsql(self.PG_URL, self.PG_SCHEMA) if self.DO_PG else load_sqlite('curr')
        self.db = TestCurrent.db

    def check_query_counts(self, clz1, clz2):
        n1 = self.db.session.query(clz1).all()
        n2 = self.db.session.query(clz2).all()
        return check_counts(n1, n2)

    def test_load(self):
        self.assertTrue(self.check_query_counts(Stop,  CurrentStops))
        self.assertTrue(self.check_query_counts(Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(RouteStop, CurrentRouteStops))
        """""
        cr_list = self.db.session.query(CurrentRoutes).all()
        for cr in cr_list:
            self.assertTrue(cr.route is not None)
        """""

    def test_routes(self):
        routes = CurrentRoutes.query_active_routes(self.db.session())
        self.assertTrue(len(routes) > 0)

    def test_stops(self):
        stops = CurrentStops.query_stops(self.db.session(), limit=1)
        self.assertTrue(len(stops) == 1)

    def test_route_stops(self):
        #import pdb; pdb.set_trace()

        # DADAN has 2 routes active now
        routes = CurrentRouteStops.unique_routes_at_stop(self.db.session(), stop_id="DADAN")
        self.assertTrue(len(routes) == 2)
        self.assertTrue(routes[0].route_id in ('NEW', 'ALWAYS'))
        self.assertTrue(routes[1].route_id in ('NEW', 'ALWAYS'))

        # DADAN has 3 routes total ... RouteStop isn't filtering current stops, so will show older inactive route
        routes = RouteStop.unique_routes_at_stop(self.db.session(), stop_id="DADAN")
        self.assertTrue(len(routes) == 3)

        # OLD is not active, so CurrentStops should not have OLD as stop in the current route stop table
        routes = CurrentRouteStops.unique_routes_at_stop(self.db.session(), stop_id="OLD")
        self.assertTrue(len(routes) == 0)

        # although OLD is not active, RouteStop should show this route stop, since it's not filtering for is_active
        routes = RouteStop.unique_routes_at_stop(self.db.session(), stop_id="OLD")
        self.assertTrue(len(routes) == 1)
        self.assertTrue(routes[0].route_id == 'ALWAYS')

    def test_stops_point(self):
        if self.DO_PG:
            point = util.Point(lat=36.915, lon=-116.762, srid="4326")
            curr_stops = CurrentStops.query_stops_via_point(self.db.session(), point)
            stops = Stop.query_stops_via_point(self.db.session(), point)
            self.assertTrue(check_counts(curr_stops, stops))

    def test_stops_bbox(self):
        if self.DO_PG:
            bbox = util.BBox(min_lat=36.0, max_lat=37.0, min_lon=-117.5, max_lon=-116.0, srid="4326")
            curr_stops = CurrentStops.query_stops_via_bbox(self.db.session, bbox)
            stops = Stop.query_stops_via_bbox(self.db.session, bbox)
            self.assertTrue(check_counts(curr_stops, stops))
