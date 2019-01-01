import os
from pkg_resources import resource_filename  # @UnresolvedImport
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import logging
log = logging.getLogger(__name__)


from gtfsdb import *
from gtfsdb.api import database_load


class TestCurrent(unittest.TestCase):

    def setUp(self):
        pass

    def check_query_counts(self, clz1, clz2):
        n1 = self.db.session.query(clz1).all()
        n2 = self.db.session.query(clz2).all()
        import pdb; pdb.set_trace()
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
        #SKIP_TESTS = True
        if SKIP_TESTS:
            log.warning("NOTE: skipping this postgres test of CurrentRoutes ... manually set SKIP_TESTS=False above")
            return True

        url = "postgresql://ott@localhost/test"
        schema = "current_test"

        path = resource_filename('gtfsdb', 'tests')
        filename = 'file:///{0}'.format(os.path.join(path, 'multi-date-feed.zip'))
        self.db = database_load(filename, url=url, schema=schema, current_tables=True)
        self.assertTrue(self.check_query_counts(Stop, CurrentStops))
        self.assertTrue(self.check_query_counts(Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(RouteStop, CurrentRouteStops))

        #import pdb; pdb.set_trace()
        cr_list = self.db.session.query(CurrentRoutes).all()
        for cr in cr_list:
            self.assertTrue(cr.route is not None)


    def test_sqlite_load(self):
        path = resource_filename('gtfsdb', 'tests')
        filename = 'file:///{0}'.format(os.path.join(path, 'multi-date-feed.zip'))
        self.db = database_load(filename, current_tables=True)
        self.assertTrue(self.check_query_counts(Stop,  CurrentStops))
        self.assertTrue(self.check_query_counts(Route, CurrentRoutes))
        self.assertTrue(self.check_query_counts(RouteStop, CurrentRouteStops))
