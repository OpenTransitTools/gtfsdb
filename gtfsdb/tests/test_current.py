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


DB=None
def load_sqlite():
    global DB
    if DB is None:
        gtfs_file = get_test_file_uri('multi-date-feed.zip')
        url = util.make_temp_sqlite_db_uri()
        # url = util.make_temp_sqlite_db_uri('curr')
        DB = database_load(gtfs_file, url=url, current_tables=True)
    return DB


class TestCurrent(unittest.TestCase):

    def setUp(self):
        #import pdb; pdb.set_trace()
        self.db = load_sqlite()

    def check_query_counts(self, clz1, clz2):
        n1 = self.db.session.query(clz1).all()
        n2 = self.db.session.query(clz2).all()
        return len(n1) != len(n2)

    def test_postgres_load(self):
        """ To run this test, do the following:
         a) emacs setup.py - uncomment install_requires='psycopg2'
         b) buildout  # need psychopg2 in bin/test script
         c) comment out "#SKIP_TESTS = True" below
         d) psql -d postgres -c "CREATE DATABASE test WITH OWNER ott;"
         e) bin/test gtfsdb.tests.test_current
        """
        SKIP_TESTS = False
        SKIP_TESTS = True
        if SKIP_TESTS:
            log.warning("NOTE: skipping this postgres test of CurrentRoutes ... manually set SKIP_TESTS=False above")
            return True

        url = "postgresql://ott@localhost/test"
        schema = "current_test"

        # import pdb; pdb.set_trace()
        gtfs_file = get_test_file_uri('multi-date-feed.zip')
        self.db = database_load(gtfs_file, url=url, schema=schema, current_tables=True)
        self.assertTrue(self.check_query_counts(Stop, CurrentStops))
        self.assertTrue(self.check_query_counts(Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(RouteStop, CurrentRouteStops))

        cr_list = self.db.session.query(CurrentRoutes).all()
        for cr in cr_list:
            self.assertTrue(cr.route is not None)

    def test_sqlite_load(self):
        self.assertTrue(self.check_query_counts(Stop,  CurrentStops))
        self.assertTrue(self.check_query_counts(Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(RouteStop, CurrentRouteStops))

    def test_routes(self):
        routes = CurrentRoutes.active_routes(self.db.session())
        self.assertTrue(len(routes) > 0)

    def test_stops(self):
        # import pdb; pdb.set_trace()
        stops = CurrentStops.query_stops(self.db.session(), limit=1)
        self.assertTrue(len(stops) == 1)
