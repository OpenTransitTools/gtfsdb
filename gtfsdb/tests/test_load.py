try:
    import unittest2 as unittest
except ImportError:
    import unittest

from . import get_test_file_uri
from gtfsdb import *
from gtfsdb.api import database_load


class TestAPI(unittest.TestCase):
    def test_database_load(self):
        gtfs_file = get_test_file_uri('sample-feed.zip')
        db = database_load(gtfs_file, ignore_blocks=True)
        self.assertTrue(len(db.session.query(Stop).all()) > 0)
        self.assertTrue(len(db.session.query(Route).all()) > 0)

