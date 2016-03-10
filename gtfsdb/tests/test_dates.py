import os
import sys
import shutil
import tempfile
import datetime
import logging
log = logging.getLogger(__name__)

from pkg_resources import resource_filename
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb import *
from gtfsdb.api import database_load

class BasicModelTests(object):
    path = resource_filename('gtfsdb', 'tests')
    gtfs_file = 'file:///{0}'.format(os.path.join(path, 'multi-date-feed.zip'))
    db_file = tempfile.mkstemp()[1]
    url = 'sqlite:///{0}'.format(db_file)
    db = database_load(gtfs_file, url=url)
    log.debug(db_file)

class TestRouteStop(unittest.TestCase, BasicModelTests):
    model = RouteStop

    def test_active_list(self):
        stops = RouteStop.active_stops(self.db.session, route_id="OCITY", direction_id="1", date=datetime.date(2015, 6, 6))
        self.assertTrue(len(stops) > 1)
        for s in stops:
            self.assertTrue("good, I see active stop id: {0}".format(s.stop_id))

    #def __init__(self): pass # uncomment for debugging via main below

def main(argv):
    shutil.copyfile(TestRouteStop.db_file, "gtfs.db")
    t = TestRouteStop()
    #import pdb; pdb.set_trace()
    t.test_active_list()

if __name__ == "__main__":
    main(sys.argv)
