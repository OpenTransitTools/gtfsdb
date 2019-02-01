try:
    import unittest2 as unittest
except ImportError:
    import unittest

import sys
import shutil
import datetime

from gtfsdb import *
from .base import load_sqlite

import logging
log = logging.getLogger(__name__)


class TestRouteStop(unittest.TestCase):
    model = RouteStop
    db = None

    def setUp(self):
        if TestRouteStop.db is None:
            TestRouteStop.db = load_sqlite()
        self.db = TestRouteStop.db

    def test_old_routes(self):
        date = datetime.date(2018, 12, 25)
        rs = RouteStop.query_active_stops(self.db.session, route_id="OLD", direction_id="1", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.query_active_stops(self.db.session, route_id="OLD", direction_id="0", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.query_active_stops(self.db.session, route_id="NEW", direction_id="1", date=date)
        self.assertTrue(len(rs) == 0)

        rs = RouteStop.query_active_stops(self.db.session, route_id="NEW", direction_id="0", date=date)
        self.assertTrue(len(rs) == 0)

    def test_via_stops(self):
        # date = datetime.date(2015, 6, 6)
        rs = RouteStop.query_by_stop(self.db.session, stop_id="OLD")
        self.assertTrue(len(rs) >= 2)

        routes = RouteStop.unique_routes_at_stop(self.db.session, stop_id="OLD")
        self.assertTrue(len(routes) == 1)

    def test_active_stop_list(self):
        rs = RouteStop.query_active_stops(self.db.session, route_id="ALWAYS", date=datetime.date(2015, 12, 25))
        self.assertTrue(len(rs) == 0)

        rs = RouteStop.query_active_stops(self.db.session, route_id="ALWAYS", date=datetime.date(2018, 12, 25))
        see_old_stop = False
        for r in rs:
            self.assertTrue(r.stop_id != "NEW")
            if r.stop_id == "OLD":
                see_old_stop = True
        self.assertTrue(see_old_stop)

        rs = RouteStop.query_active_stops(self.db.session, route_id="ALWAYS", date=datetime.date(2019, 1, 5))
        see_new_stop = False
        for r in rs:
            self.assertTrue(r.stop_id != "OLD")
            if r.stop_id == "NEW":
                see_new_stop = True
        self.assertTrue(see_new_stop)

    def test_stop_dates(self):
        active = RouteStop.is_stop_active(self.db.session, stop_id="OLD", date=datetime.date(2018, 12, 25))
        self.assertTrue(active)

        active = RouteStop.is_stop_active(self.db.session, stop_id="OLD", date=datetime.date(2019, 1, 3))
        self.assertFalse(active)

        active = RouteStop.is_stop_active(self.db.session, stop_id="OLD", date=datetime.date(2019, 6, 6))
        self.assertFalse(active)

        active = RouteStop.is_stop_active(self.db.session, stop_id="NEW", date=datetime.date(2018, 12, 25))
        self.assertFalse(active)

        active = RouteStop.is_stop_active(self.db.session, stop_id="NEW", date=datetime.date(2019, 6, 6))
        self.assertTrue(active)

    def test_new_routes(self):
        date = datetime.date(2019, 1, 1)
        rs = RouteStop.query_active_stops(self.db.session, route_id="NEW", direction_id="1", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.query_active_stops(self.db.session, route_id="NEW", direction_id="0", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.query_active_stops(self.db.session, route_id="OLD", direction_id="1", date=date)
        self.assertTrue(len(rs) == 0)

        rs = RouteStop.query_active_stops(self.db.session, route_id="OLD", direction_id="0", date=date)
        self.assertTrue(len(rs) == 0)

    def test_effective_dates(self):
        date = datetime.date(2019, 1, 1)
        rs = RouteStop.query_active_stops(self.db.session, route_id="NEW", direction_id="1", date=date)
        self.assertTrue(len(rs) > 2)

    def test_active_list(self):
        rs = RouteStop.query_active_stops(self.db.session, route_id="OLD", direction_id="1", date=datetime.date(2018, 12, 25))
        self.assertTrue(len(rs) > 1)
        for s in rs:
            self.assertTrue("good, I see active stop id: {0}".format(s.stop_id))


def main(argv):
    shutil.copyfile(TestRouteStop.db_file, "gtfs.db")
    t = TestRouteStop()
    t.test_active_list()

if __name__ == "__main__":
    main(sys.argv)
