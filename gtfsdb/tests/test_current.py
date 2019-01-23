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
        gtfs_file = get_test_file_uri('multi-date-feed.zip')
        url = util.make_temp_sqlite_db_uri()
        # url = util.make_temp_sqlite_db_uri('curr')
        DB = database_load(gtfs_file, url=url, current_tables=True)
    return DB

PGDB = None
def load_pgsql(skip):
    global PGDB
    if not skip and PGDB is None:
        # import pdb; pdb.set_trace()
        url = "postgresql+psycopg2://ott@maps7:5432/ott"
        #url = "postgresql://ott@localhost/test"
        schema = "current_test"
        gtfs_file = get_test_file_uri('multi-date-feed.zip')
        PGDB = database_load(gtfs_file, url=url, schema=schema, is_geospatial=True, current_tables=True)
    return PGDB


class TestCurrent(unittest.TestCase):
    SKIP_PG_TESTS = False
    SKIP_PG_TESTS = True

    def setUp(self):
        #import pdb; pdb.set_trace()
        self.db = load_sqlite()
        self.pgdb = load_pgsql(self.SKIP_PG_TESTS)

    def check_query_counts(self, db, clz1, clz2):
        n1 = db.session.query(clz1).all()
        n2 = db.session.query(clz2).all()
        return len(n1) != len(n2)

    def test_postgres_load(self):
        """ To run this test, do the following:
         a) emacs setup.py - uncomment install_requires='psycopg2'
         b) buildout  # need psychopg2 in bin/test script
         c) comment out "#SKIP_TESTS = True" below
         d) psql -d postgres -c "CREATE DATABASE test WITH OWNER ott;"
         e) bin/test gtfsdb.tests.test_current
        """
        if self.SKIP_PG_TESTS:
            log.warning("NOTE: skipping this postgres test of CurrentRoutes ... manually set SKIP_TESTS=False above")
            return True

        self.assertTrue(self.check_query_counts(self.pgdb, Stop, CurrentStops))
        self.assertTrue(self.check_query_counts(self.pgdb, Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(self.pgdb, RouteStop, CurrentRouteStops))

        cr_list = self.pgdb.session.query(CurrentRoutes).all()
        for cr in cr_list:
            self.assertTrue(cr.route is not None)

    def test_sqlite_load(self):
        self.assertTrue(self.check_query_counts(self.db, Stop,  CurrentStops))
        self.assertTrue(self.check_query_counts(self.db, Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(self.db, RouteStop, CurrentRouteStops))

    def test_routes(self):
        routes = CurrentRoutes.active_routes(self.db.session())
        self.assertTrue(len(routes) > 0)

    def test_stops(self):
        stops = CurrentStops.query_stops(self.db.session(), limit=1)
        self.assertTrue(len(stops) == 1)

    def test_stops_point(self):
        point = util.Point(lat=45.5, lon=-122.5)
        #stops = CurrentStops.query_stops_via_point(self.db.session(), point)
        #self.assertTrue(len(stops) == 1)

    def test_stops_bbox(self):
        # import pdb; pdb.set_trace()
        bbox = util.BBox(min_lat=44.4, max_lat=44.4, min_lon=-122.5, max_lon=-122.5)
        #stops = CurrentStops.query_stops_via_bbox(session, bbox)
        #self.assertTrue(len(stops) == 1)


