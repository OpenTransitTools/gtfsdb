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

        path = resource_filename('gtfsdb', 'tests')
        filename = 'file:///{0}'.format(os.path.join(path, 'multi-date-feed.zip'))
        self.db = database_load(filename, url=url, schema=schema, populate_current=True)

    def test_sqlite_load(self):
        path = resource_filename('gtfsdb', 'tests')
        filename = 'file:///{0}'.format(os.path.join(path, 'multi-date-feed.zip'))
        self.db = database_load(filename, populate_current=True)
