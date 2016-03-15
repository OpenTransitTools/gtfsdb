import os
import sys
import shutil
import tempfile
import datetime
import logging
log = logging.getLogger(__name__)

from pkg_resources import resource_filename
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb import *
from gtfsdb.api import database_load

class BasicModelTests(object):
    path = resource_filename('gtfsdb', 'tests')
    gtfs_file = 'file:///{0}'.format(os.path.join(path, 'multi-date-feed.zip'))
    db_file = tempfile.mkstemp()[1]
    url = 'sqlite:///{0}'.format(db_file)
    db = database_load(gtfs_file, url=url)
    log.debug(db_file)

class TestRouteStop(unittest.TestCase, BasicModelTests):
    model = RouteStop

    def test_old_routes(self):
        date = datetime.date(2015, 6, 6)
        rs = RouteStop.active_stops(self.db.session, route_id="OLD", direction_id="1", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.active_stops(self.db.session, route_id="OLD", direction_id="0", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.active_stops(self.db.session, route_id="NEW", direction_id="1", date=date)
        self.assertTrue(len(rs) == 0)

        rs = RouteStop.active_stops(self.db.session, route_id="NEW", direction_id="0", date=date)
        self.assertTrue(len(rs) == 0)

    def test_via_stops(self):
        #date = datetime.date(2015, 6, 6)
        rs = RouteStop.query_by_stop(self.db.session, stop_id="OLD")
        self.assertTrue(len(rs) >= 2)

        routes = RouteStop.unique_routes_at_stop(self.db.session, stop_id="OLD")
        self.assertTrue(len(routes) == 1)

    def test_routes_via_stop(self):
        routes = RouteStop.unique_routes_at_stop(self.db.session, stop_id="STAGECOACH", route_name_filter=True)
        self.assertTrue(len(routes) == 3)

    def test_new_routes(self):
        date = datetime.date(2016, 6, 6)
        rs = RouteStop.active_stops(self.db.session, route_id="NEW", direction_id="1", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.active_stops(self.db.session, route_id="NEW", direction_id="0", date=date)
        self.assertTrue(len(rs) > 2)

        rs = RouteStop.active_stops(self.db.session, route_id="OLD", direction_id="1", date=date)
        self.assertTrue(len(rs) == 0)

        rs = RouteStop.active_stops(self.db.session, route_id="OLD", direction_id="0", date=date)
        self.assertTrue(len(rs) == 0)


    def test_active_list(self):
        rs = RouteStop.active_stops(self.db.session, route_id="OLD", direction_id="1", date=datetime.date(2015, 6, 6))
        self.assertTrue(len(rs) > 1)
        for s in rs:
            self.assertTrue("good, I see active stop id: {0}".format(s.stop_id))

    #def __init__(self): pass # uncomment for debugging via main below

def main(argv):
    shutil.copyfile(TestRouteStop.db_file, "gtfs.db")
    t = TestRouteStop()
    #import pdb; pdb.set_trace()
    t.test_active_list()
    #t.test_old_stops()

if __name__ == "__main__":
    main(sys.argv)
