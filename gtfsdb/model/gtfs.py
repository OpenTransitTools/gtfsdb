from contextlib import closing
import logging
import os
import time
import pkg_resources
import shutil
import subprocess
import sys
import tempfile
from urllib import urlretrieve
import zipfile

from .agency import Agency
from .calendar import Calendar, CalendarDate, UniversalCalendar
from .fare import FareAttribute, FareRule
from .feed_info import FeedInfo
from .frequency import Frequency
from .route import Route, RouteType
from .shape import Pattern, Shape
from .stop_time import StopTime
from .stop import Stop
from .stop_feature import StopFeature, StopFeatureType
from .transfer import Transfer
from .trip import Trip


log = logging.getLogger(__name__)


class GTFS(object):

    def __init__(self, filename):
        self.file = filename
        self.local_file = urlretrieve(filename)[0]

    def load(self, db):
        """Load GTFS into database"""
        log.debug('begin load')
        gtfs_directory = self.unzip()
        data_directory = pkg_resources.resource_filename('gtfsdb', 'data')

        # load lookup tables first
        RouteType.load(db.engine, data_directory, False)
        StopFeatureType.load(db.engine, data_directory, False)

        # load GTFS data files & transform/derive additional data
        # due to foreign key constraints these files need to be loaded in the appropriate order
        FeedInfo.load(db.engine, gtfs_directory)
        Agency.load(db.engine, gtfs_directory)
        Calendar.load(db.engine, gtfs_directory)
        CalendarDate.load(db.engine, gtfs_directory)
        Route.load(db.engine, gtfs_directory)
        Stop.load(db.engine, gtfs_directory)
        StopFeature.load(db.engine, gtfs_directory)
        Transfer.load(db.engine, gtfs_directory)
        Shape.load(db.engine, gtfs_directory)
        Pattern.load(db.engine)
        Trip.load(db.engine, gtfs_directory)
        StopTime.load(db.engine, gtfs_directory)
        Frequency.load(db.engine, gtfs_directory)
        FareAttribute.load(db.engine, gtfs_directory)
        FareRule.load(db.engine, gtfs_directory)
        shutil.rmtree(gtfs_directory)
        UniversalCalendar.load(db.engine)

        # load derived geometries
        # currently only written for postgresql
        dialect_name = db.engine.url.get_dialect().name
        if db.is_geospatial and dialect_name == 'postgresql':
            s = ' - %s geom' % (Route.__tablename__)
            sys.stdout.write(s)
            start_seconds = time.time()
            session = db.get_session()
            q = session.query(Route)
            for route in q:
                route.load_geometry(session)
                session.merge(route)
            session.commit()
            session.close()
            process_time = time.time() - start_seconds
            print ' (%.0f seconds)' % (process_time)
        log.debug('end load')

    def validate(self):
        """Run transitfeed.feedvalidator"""
        path = os.path.join(
            pkg_resources.get_distribution('transitfeed').egg_info,
            'scripts/feedvalidator.py')

        stdout, stderr = subprocess.Popen(
            [sys.executable, path, '--output=CONSOLE', self.local_file],
            stdout=subprocess.PIPE
        ).communicate()

        is_valid = True
        for line in str(stdout).splitlines():
            if line.startswith('ERROR'):
                is_valid = 'errors' not in line.lower()
                continue
        return is_valid, stdout

    def unzip(self, path=None):
        """Unzip GTFS files from URL/directory to path."""
        path = path if path else tempfile.mkdtemp()
        with closing(zipfile.ZipFile(self.local_file)) as z:
            z.extractall(path)
        return path
