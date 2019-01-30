try:
    import unittest2 as unittest
except ImportError:
    import unittest

from .base import check_counts
from gtfsdb import *

import logging
log = logging.getLogger(__name__)


class TestGeomQueries(unittest.TestCase):
    """
    load current tables:
    bin/gtfsdb-current-load -g -s trimet -d postgresql://ott@localhost:5432/ott x
    """
    db = None
    DO_PG = False

    def setUp(self):
        from .test_current import TestCurrent
        if TestCurrent.DO_PG and TestGeomQueries.db is None:
            self.DO_PG = True
            self.db = Database(url=TestCurrent.PG_URL, schema=TestCurrent.PG_SCHEMA, is_geospatial=True, current_tables=True)

    def test_nearest(self):
        if self.DO_PG:
            point = util.Point(lat=45.53, lon=-122.6664, srid="4326")
            curr_stops = CurrentStops.query_stops_via_point(self.db.session(), point)
            stops = Stop.query_stops_via_point(self.db.session(), point)
            self.assertTrue(check_counts(curr_stops, stops))

    def test_bbox(self):
        if self.DO_PG and False:
            #import pdb; pdb.set_trace()
            bbox = util.BBox(min_lat=45.530, max_lat=45.535, min_lon=-122.665, max_lon=-122.667, srid="4326")
            curr_stops = CurrentStops.query_stops_via_bbox(self.db.session, bbox)
            stops = Stop.query_stops_via_bbox(self.db.session, bbox)
            self.assertTrue(check_counts(curr_stops, stops))
