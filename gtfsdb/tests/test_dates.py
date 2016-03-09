import logging
log = logging.getLogger(__name__)

import datetime
import os
import tempfile
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
    url = 'sqlite:///{0}'.format(tempfile.mkstemp()[1])
    log.debug(url)
    db = database_load(gtfs_file, url=url)

class TestRouteStop(unittest.TestCase, BasicModelTests):
    model = RouteStop

    def test_active_list(self):
        #import pdb; pdb.set_trace()
        stops = RouteStop.active_stops(self.db.session, route_id="OCITY", direction_id="1", date=datetime.date(2015, 6, 6))
        #self.assertTrue(len(stops) > 1)
        for s in stops:
            self.assertTrue("good, I see active stop id: {0}".format(s.stop_id))

