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

    def test_entity(self):
        if hasattr(self, 'model'):
            for r in self.db.session.query(self.model).limit(5):
                self.assert_(isinstance(r, self.model))


class TestStop(unittest.TestCase, BasicModelTests):

    model = Stop

    def test_headsigns(self):
        stop = self.db.session.query(Stop).first()
        print stop.headsigns

    def test_trips(self):
        stop = self.db.session.query(Stop).first()
        for t in stop.trips:
            self.assert_(isinstance(t, Trip))
