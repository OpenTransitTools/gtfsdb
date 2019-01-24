try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb import *
from gtfsdb import util
from gtfsdb.api import database_load
from . import get_test_file_uri

import logging
log = logging.getLogger(__name__)

DB = None
def load_sqlite():
    global DB
    if DB is None:
        #import pdb; pdb.set_trace()
        gtfs_file = get_test_file_uri('multi-date-feed.zip')
        url = util.make_temp_sqlite_db_uri()
        # url = util.make_temp_sqlite_db_uri('curr')
        DB = database_load(gtfs_file, url=url, current_tables=True)
    return DB

PGDB = None
def load_pgsql():
    """ To run this test, do the following:
     x) bin/test  gtfsdb.tests.test_current

     You might also have to do the following:
     a) emacs setup.py - uncomment install_requires='psycopg2'
     b) buildout  # need psychopg2 in bin/test script
     c) comment out "#SKIP_TESTS = True" below
     d) psql -d postgres -c "CREATE DATABASE test WITH OWNER ott;"
     e) bin/test gtfsdb.tests.test_current
    """
    global PGDB
    if PGDB is None:
        # import pdb; pdb.set_trace()
        url = "postgresql+psycopg2://ott@maps7:5432/ott"
        #url = "postgresql://ott@localhost/test"
        schema = "current_test"
        gtfs_file = get_test_file_uri('multi-date-feed.zip')
        PGDB = database_load(gtfs_file, url=url, schema=schema, is_geospatial=True, current_tables=True)
    return PGDB


class TestCurrent(unittest.TestCase):
    db = None
    DO_PG = True #False

    def setUp(self):
        self.db = load_pgsql() if self.DO_PG else load_sqlite()

    def check_query_counts(self, clz1, clz2):
        n1 = self.db.session.query(clz1).all()
        n2 = self.db.session.query(clz2).all()
        return len(n1) != len(n2) and len(n1) > 0 and len(n2) > 0

    def test_sqlite_load(self):
        self.assertTrue(self.check_query_counts(Stop,  CurrentStops))
        self.assertTrue(self.check_query_counts(Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(RouteStop, CurrentRouteStops))
        """""
        cr_list = self.db.session.query(CurrentRoutes).all()
        for cr in cr_list:
            self.assertTrue(cr.route is not None)
        """""

    def test_routes(self):
        routes = CurrentRoutes.active_routes(self.db.session())
        self.assertTrue(len(routes) > 0)

    def test_stops(self):
        stops = CurrentStops.query_stops(self.db.session(), limit=1)
        self.assertTrue(len(stops) == 1)

    def test_stops_point(self):
        point = util.Point(lat=36.915, lon=-116.762, srid="4326")
        #stops = CurrentStops.query_stops_via_point(self.db.session(), point)
        stops = Stop.query_stops_via_point(self.db.session(), point)
        self.assertTrue(len(stops) > 1)

    def test_stops_bbox(self):
        # import pdb; pdb.set_trace()
        bbox = util.BBox(min_lat=36.0, max_lat=37.0, min_lon=-117.5, max_lon=-116.0, srid="4326")
        #stops = CurrentStops.query_stops_via_bbox(self.db.session, bbox)
        stops = Stop.query_stops_via_bbox(self.db.session, bbox)
        self.assertTrue(len(stops) > 1)


