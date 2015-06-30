import datetime
import logging
import os
from pkg_resources import resource_filename  # @UnresolvedImport
import tempfile
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb import *
from gtfsdb.api import database_load


log = logging.getLogger(__name__)


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

    def test_active_routes(self):
        if hasattr(self, 'model'):
            for r in self.db.session.query(self.model).all():
                print "{} {} {} {}".format(r.route_id, r.agency_id, r.start_date, r.end_date)

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
