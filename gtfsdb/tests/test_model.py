from gtfsdb import *
from .base import load_sqlite

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime
import logging
log = logging.getLogger(__name__)


class BasicModelTests(object):
    db = load_sqlite(gtfs_name='large-sample-feed.zip')

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
                self.assertTrue(isinstance(r, self.model))


class TestRoute(unittest.TestCase, BasicModelTests):
    model = Route

    def test_dates(self):
        m = self.get_first()
        self.assertTrue(isinstance(m.start_date, datetime.date))
        self.assertTrue(isinstance(m.end_date, datetime.date))

    def test_active_date(self):
        # import pdb; pdb.set_trace()
        routes = Route.query_active_routes(self.db.session, datetime.date(2014, 6, 6))
        self.assertTrue(len(routes) > 1)
        for r in routes:
            self.assertTrue("good, I see active route id: {0}".format(r.route_id))

    def test_active_today(self):
        routes = Route.query_active_routes(self.db.session)
        for r in routes:
            self.assertFalse("we should not have any routes, but I see route id: {0}".format(r.route_id))


class TestRouteStop(unittest.TestCase, BasicModelTests):
    model = RouteStop

    def test_active_list(self):
        stops = RouteStop.query_active_stops(self.db.session, route_id="194", direction_id="1", date=datetime.date(2014, 6, 6))
        self.assertTrue(len(stops) > 1)
        for s in stops:
            self.assertTrue("good, I see active stop id: {0}".format(s.stop_id))

    def test_by_stop(self):
        stops = RouteStop.query_by_stop(self.db.session, stop_id="12883")
        self.assertTrue(len(stops) >= 1)

    def test_routes_serving_stop(self):
        routes = RouteStop.query_by_stop(self.db.session, stop_id="10767")
        self.assertTrue(len(routes) == 2)

    def test_route_stops(self):
        date = datetime.date(2014, 6, 6)
        stops = RouteStop.query_active_stops(self.db.session, route_id="193", direction_id="1", date=date)
        self.assertTrue(len(stops) > 5)

        stops = RouteStop.query_active_stops(self.db.session, route_id="193", direction_id="0", date=date)
        self.assertTrue(len(stops) > 5)

        stops = RouteStop.query_active_stops(self.db.session, route_id="194", direction_id="1", date=date)
        self.assertTrue(len(stops) > 5)

        stops = RouteStop.query_active_stops(self.db.session, route_id="194", direction_id="0", date=date)
        self.assertTrue(len(stops) > 5)

    def test_active_date(self):
        m = self.get_first()
        self.assertTrue(m.is_active(datetime.date(2014, 6, 6)))

    def test_active_today(self):
        m = self.get_first()
        self.assertFalse(m.is_active())


class TestRouteDirection(unittest.TestCase, BasicModelTests):
    model = RouteDirection


class TestTrip(unittest.TestCase, BasicModelTests):
    model = Trip

    def test_end_stop(self):
        m = self.get_first()
        self.assertTrue(isinstance(m.end_stop, Stop))

    def test_start_stop(self):
        m = self.get_first()
        self.assertTrue(isinstance(m.start_stop, Stop))

    def test_stop_times(self):
        m = self.get_first()
        for stop_time in m.stop_times:
            self.assertTrue(isinstance(stop_time, StopTime))

    def test_times(self):
        m = self.get_first()
        self.assertTrue(m.start_time)
        self.assertTrue(m.end_time)


class TestStop(unittest.TestCase, BasicModelTests):
    model = Stop

    def test_headsigns(self):
        m = self.get_first()
        self.assertTrue(isinstance(m.headsigns, dict))

    def test_routes(self):
        m = self.get_first()
        for r in m.routes:
            self.assertTrue(isinstance(r, Route))


class TestStopTimes(unittest.TestCase, BasicModelTests):
    model = StopTime

    def test_shape_pt_dist(self):
        """ the large-sample-feed.zip lacks the optional 'shape_dist_traveled' attribute, so provide it post-process """
        num = -0.1
        for s in self.db.session.query(StopTime).filter(StopTime.trip_id == '4383758').all():
            self.assertTrue(s.shape_dist_traveled > num)
            num += 1.0


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


class TestShape(unittest.TestCase, BasicModelTests):
    model = Shape

    def test_shape_pt_dist(self):
        """ the large-sample-feed.zip lacks the optional 'shape_dist_traveled' attribute, so provide it post-process """
        num = -0.1
        for s in self.db.session.query(self.model).limit(5):
            self.assertTrue(s.shape_dist_traveled > num)
            num += 1.0


class TestTransfer(unittest.TestCase, BasicModelTests):
    model = Transfer

