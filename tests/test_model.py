__author__ = 'rhunter'
import unittest
import os

import testing.postgresql

from gtfsdb.api import database_load
from gtfsdb.model.db import Database
from gtfsdb.model.agency import Agency
from gtfsdb.model.fare import FareAttribute, FareRule
from gtfsdb.model.calendar import Calendar, CalendarDate
from gtfsdb.model.frequency import Frequency
from gtfsdb.model.route import Route
from gtfsdb.model.shape import Shape
from gtfsdb.model.stop import Stop
from gtfsdb.model.stop_time import StopTime
from gtfsdb.model.trip import Trip

class TestModel(unittest.TestCase):
    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        self.database = Database(url=self.postgresql.url())
        self.database.engine.execute('create extension postgis;')
        self.database.engine.execute('create extension postgis_topology;')
        self.database.create()
        self.root_dir = os.path.dirname(__file__)

    def tearDown(self):
        self.database.session_factory.close_all()
        self.postgresql.stop()

    def test_import_feed(self):
        database_load(os.path.join(self.root_dir, 'data/sample-feed.zip'), db_url=self.postgresql.url())
        session = self.database.get_session()
        self.assertEqual(1, session.query(Agency).count())
        self.assertEqual(2, session.query(Calendar).count())
        self.assertEqual(1, session.query(CalendarDate).count())
        self.assertEqual(2, session.query(FareAttribute).count())
        self.assertEqual(4, session.query(FareRule).count())
        self.assertEqual(11, session.query(Frequency).count())
        self.assertEqual(5, session.query(Route).count())
        self.assertEqual(223, session.query(Shape).count())
        self.assertEqual(28, session.query(StopTime).count())
        self.assertEqual(9, session.query(Stop).count())
        self.assertEqual(11, session.query(Trip).count())


