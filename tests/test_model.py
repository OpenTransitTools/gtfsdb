__author__ = 'rhunter'
import unittest
import os
import hashlib

import testing.postgresql
from geoalchemy2.functions import ST_AsText, ST_X, ST_Y

from gtfsdb.api import database_load, create_shapes_geoms, database_load_versioned
from gtfsdb.model.db import Database
from gtfsdb.model.agency import Agency
from gtfsdb.model.metaTracking import FeedFile
from gtfsdb.model.calendar import Calendar, CalendarDate
from gtfsdb.model.frequency import Frequency
from gtfsdb.model.route import Route
from gtfsdb.model.shape import Shape, ShapeGeom
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
        file_location = os.path.join(self.root_dir, 'data/sample-feed.zip')
        md5 = hashlib.md5(open(file_location, 'rb').read()).hexdigest()
        feed_file=FeedFile(md5sum=md5, file_url=file_location)
        database_load_versioned(feed_file, self.postgresql.url())

    def tearDown(self):
        self.database.session_factory.close_all()
        self.postgresql.stop()

    def test_agency_delete(self):
        session = self.database.get_session()
        agency = session.query(Agency).first()
        self.assertTrue(agency)
        session.delete(agency)
        session.commit()
        for table_cls in self.database.classes:
            if table_cls == FeedFile:
                continue
            self.assertEqual(0, session.query(table_cls).count(),
                             "Failed on table {}".format(table_cls))

    def test_create_geoms(self):
        create_shapes_geoms(db_url=self.postgresql.url())
        session = self.database.get_session()
        self.assertEqual(1, session.query(ShapeGeom).count())
        session.query(ST_AsText(ShapeGeom.the_geom)).one()

    def test_import_feed(self):
        session = self.database.get_session()
        self.assertEqual(1, session.query(Agency).count())
        self.assertEqual(2, session.query(Calendar).count())
        self.assertEqual(1, session.query(CalendarDate).count())
        #self.assertEqual(2, session.query(FareAttribute).count())
        #self.assertEqual(4, session.query(FareRule).count())
        self.assertEqual(11, session.query(Frequency).count())
        self.assertEqual(5, session.query(Route).count())
        self.assertEqual(223, session.query(Shape).count())
        self.assertEqual(28, session.query(StopTime).count())
        self.assertEqual(9, session.query(Stop).count())
        self.assertEqual(11, session.query(Trip).count())

        for lon, lat, x, y in session.query(Stop.stop_lon, Stop.stop_lat, ST_X(Stop.the_geom), ST_Y(Stop.the_geom)).all():
            self.assertEqual(float(lon), x)
            self.assertEqual(float(lat), y)

        for lon, lat, x, y in session.query(Shape.shape_pt_lon, Shape.shape_pt_lat, ST_X(Shape.the_geom), ST_Y(Shape.the_geom)).all():
            self.assertAlmostEqual(float(lon), x)
            self.assertAlmostEqual(float(lat), y)

    def test_create_and_remove_index(self):
        self.database.drop_indexes()
        self.database.create_indexes()



