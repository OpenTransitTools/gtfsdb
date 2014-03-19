import os
from pkg_resources import resource_filename  # @UnresolvedImport
import sys
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

from gtfsdb import *


class BasicModelTests(object):
    path = resource_filename('gtfsdb', 'tests')
    url = 'sqlite:///{0}'.format(os.path.join(path, 'sample_feed.db'))
    db = Database(url=url)

    def get_first(self):
        if hasattr(self, 'model'):
            return self.db.session.query(self.model).first()

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


class TestRoute(unittest.TestCase, BasicModelTests):
    model = Route


class TestShape(unittest.TestCase, BasicModelTests):
    model = Shape


class TestStop(unittest.TestCase, BasicModelTests):
    model = Stop

    def test_headsigns(self):
        m = self.get_first()
        m.headsigns


class TestStopTimes(unittest.TestCase, BasicModelTests):
    model = StopTime


class TestTransfer(unittest.TestCase, BasicModelTests):
    model = Transfer


class TestTrip(unittest.TestCase, BasicModelTests):
    model = Trip
