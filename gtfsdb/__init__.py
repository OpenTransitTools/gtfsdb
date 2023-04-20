from gtfsdb.model.db import Database
from gtfsdb.model.gtfs import GTFS

from gtfsdb.model.agency import Agency  # noqa
from gtfsdb.model.calendar import *  # noqa
from gtfsdb.model.fare import *  # noqa
from gtfsdb.model.feed_info import FeedInfo  # noqa
from gtfsdb.model.frequency import Frequency  # noqa
from gtfsdb.model.route import *  # noqa
from gtfsdb.model.route_stop import *  # noqa
from gtfsdb.model.shape import *  # noqa
from gtfsdb.model.pattern import *  # noqa
from gtfsdb.model.pattern_base import *  # noqa
from gtfsdb.model.stop import *  # noqa
from gtfsdb.model.stop_feature import *  # noqa
from gtfsdb.model.stop_time import StopTime  # noqa
from gtfsdb.model.transfer import Transfer  # noqa
from gtfsdb.model.translation import Translation # noqa
from gtfsdb.model.trip import Trip  # noqa
from gtfsdb.model.block import Block  # noqa


SORTED_CLASS_NAMES = [
    RouteType.__name__,
    RouteFilter.__name__,
    FeedInfo.__name__,
    Agency.__name__,
    Block.__name__,
    Calendar.__name__,
    CalendarDate.__name__,
    Route.__name__,
    RouteDirection.__name__,
    Stop.__name__,
    StopFeature.__name__,
    Transfer.__name__,
    Shape.__name__,
    Pattern.__name__,
    PatternBase.__name__,
    Trip.__name__,
    StopTime.__name__,
    RouteStop.__name__,
    Frequency.__name__,
    FareAttribute.__name__,
    FareRule.__name__,
    UniversalCalendar.__name__,
    Translation.__name__,
]


CURRENT_CLASS_NAMES = [
    CurrentRoutes.__name__,
    CurrentRouteStops.__name__,
    CurrentStops.__name__,
]