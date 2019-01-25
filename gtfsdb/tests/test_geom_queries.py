try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb import *

import logging
log = logging.getLogger(__name__)


class TestGeomQueries(unittest.TestCase):
    """
    load current tables:
    bin/gtfsdb-current-load -g -s trimet -d postgresql://ott@localhost/ott x
    """
    db = None
    DO_PG = True  # False

    def setUp(self):
        url = "postgresql://ott@localhost/ott"
        schema = "trimet"
        if self.DO_PG:
            self.db = Database(url=url, schema=schema, is_geospatial=True, current_tables=True)

    @classmethod
    def check_counts(cls, n1, n2):
        ret_val = len(n1) != len(n2) and len(n1) > 0 and len(n2) > 0
        return ret_val

    @classmethod
    def print_stops(cls, stop_list):
        for s in stop_list:
            print(s.__dict__)

    def test_nearest(self):
        if self.DO_PG:
            point = util.Point(lat=45.53, lon=-122.6664, srid="4326")
            curr_stops = CurrentStops.query_stops_via_point(self.db.session(), point)
            stops = Stop.query_stops_via_point(self.db.session(), point)
            #self.assertTrue(self.check_counts(curr_stops, stops))
            self.print_stops(curr_stops)
            #self.print_stops(stops)

    def test_bbox(self):
        if self.DO_PG and False:
            #import pdb; pdb.set_trace()
            bbox = util.BBox(min_lat=45.530, max_lat=45.535, min_lon=-122.665, max_lon=-122.667, srid="4326")
            curr_stops = CurrentStops.query_stops_via_bbox(self.db.session, bbox)
            stops = Stop.query_stops_via_bbox(self.db.session, bbox)
            self.assertTrue(self.check_counts(curr_stops, stops))
            self.print_stops(curr_stops)
            self.print_stops(stops)
