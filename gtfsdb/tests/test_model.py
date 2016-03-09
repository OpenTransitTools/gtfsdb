import logging
log = logging.getLogger(__name__)

import datetime
import os
import tempfile
from pkg_resources import resource_filename  # @UnresolvedImport

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb import *
from gtfsdb.api import database_load

class BasicModelTests(object):

    path = resource_filename('gtfsdb', 'tests')
    gtfs_file = 'file:///{0}'.format(os.path.join(path, 'large-sample-feed.zip'))
    url = 'sqlite:///{0}'.format(tempfile.mkstemp()[1])
    log.debug(url)
    db = database_load(gtfs_file, url=url)

    def get_first(self):
        try:
            self._first
        except AttributeError:
            if hasattr(self, 'model'):
                self._first = self.db.session.query(self.model).first()
                return self._first

    def test_entity(self):
        if hasattr(self, 'model'):
            for r in self.db.session.query(self.model).limit(5):
                self.assert_(isinstance(r, self.model))


class TestAgency(unittest.TestCase, BasicModelTests):
    model = Agency


class TestCalendar(unittest.TestCase, BasicModelTests):
    model = Calendar


class TestCalendarDate(unittest.TestCase, BasicModelTests):
    model = CalendarDate


class TestFareAttribute(unittest.TestCase, BasicModelTests):
    model = FareAttribute


class TestFareRule(unittest.TestCase, BasicModelTests):
    model = FareRule


class TestRoute(unittest.TestCase, BasicModelTests):
    model = Route

    def test_dates(self):
        m = self.get_first()
        self.assert_(isinstance(m.start_date, datetime.date))
        self.assert_(isinstance(m.end_date, datetime.date))

    def test_active_date(self):
        routes = Route.active_routes(self.db.session, datetime.date(2014, 6, 6))
        for r in routes:
            self.assertTrue("good, I see active route id: {0}".format(r.route_id))

    def test_active_today(self):
        routes = Route.active_routes(self.db.session)
        for r in routes:
            self.assertFalse("we should not have any routes, but I see route id: {0}".format(r.route_id))

class TestRouteStop(unittest.TestCase, BasicModelTests):
    model = RouteStop

    def test_active_date(self):
        #import pdb; pdb.set_trace()
        m = self.get_first()
        self.assertTrue(m.is_active(datetime.date(2014, 6, 6)))

    def test_active_today(self):
        m = self.get_first()
        self.assertFalse(m.is_active())

class TestRouteDirection(unittest.TestCase, BasicModelTests):
    model = RouteDirection

class TestShape(unittest.TestCase, BasicModelTests):
    model = Shape

class TestStop(unittest.TestCase, BasicModelTests):
    model = Stop

    def test_headsigns(self):
        m = self.get_first()
        self.assert_(isinstance(m.headsigns, dict))

    def test_routes(self):
        m = self.get_first()
        for r in m.routes:
            self.assert_(isinstance(r, Route))

class TestStopTimes(unittest.TestCase, BasicModelTests):
    model = StopTime

class TestTransfer(unittest.TestCase, BasicModelTests):
    model = Transfer

class TestTrip(unittest.TestCase, BasicModelTests):
    model = Trip

    def test_end_stop(self):
        m = self.get_first()
        self.assert_(isinstance(m.end_stop, Stop))

    def test_start_stop(self):
        m = self.get_first()
        self.assert_(isinstance(m.start_stop, Stop))

    def test_stop_times(self):
        m = self.get_first()
        for stop_time in m.stop_times:
            self.assert_(isinstance(stop_time, StopTime))

    def test_times(self):
        m = self.get_first()
        self.assert_(m.start_time)
        self.assert_(m.end_time)
