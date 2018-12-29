import os
from pkg_resources import resource_filename  # @UnresolvedImport
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import logging
log = logging.getLogger(__name__)

SKIP_TESTS = False
SKIP_TESTS = True


""" To run this test, do the following:
 a) emacs setup.py - uncomment install_requires='psycopg2'
 b) comment out "#SKIP_TESTS = True" above 
 c) psql -d postgres -c "CREATE DATABASE test WITH OWNER ott;"
 d) buildout # need psychopg2 in bin/test script
 e) bin/test gtfsdb.tests.test_materalized_view
"""
import sqlalchemy as db
from gtfsdb import config
from gtfsdb.api import database_load
from gtfsdb.model.base import Base
from gtfsdb.model.route import Route


class TestMaterialziedView(unittest.TestCase):

    def setUp(self):
        pass

    def test_database_load(self):
        if SKIP_TESTS:
            log.warning("NOTE: skipping this Postgres-only test of Materalized Views ... manually set SKIP_TESTS=False above")
            return True

        url = "postgresql://ott@localhost/test"
        schema = "current_test"

        class RRR(Route):
            datasource = config.DATASOURCE_DERIVED
            __tablename__ = 'rrr'

            def update_view(self):
                pass

        db.Index(RRR.__name__ + '_index', RRR.route_id, unique=True)

        config.SORTED_CLASS_NAMES.append(RRR.__name__)
        e = db.create_engine(url, echo=True)
        Base.metadata.drop_all(e, checkfirst=True)

        path = resource_filename('gtfsdb', 'tests')
        filename = 'file:///{0}'.format(os.path.join(path, 'multi-date-feed.zip'))
        self.db = database_load(filename, url=url, schema=schema)
