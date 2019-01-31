try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb import *
from .base import load_sqlite


class TestLoad(unittest.TestCase):
    db = None

    def setUp(self):
        if TestLoad.db is None:
            TestLoad.db = load_sqlite(gtfs_name='sample-feed.zip')
        self.db = TestLoad.db

    def test_database_load(self):
        self.assertTrue(len(self.db.session.query(Stop).all()) > 0)
        self.assertTrue(len(self.db.session.query(Route).all()) > 0)
