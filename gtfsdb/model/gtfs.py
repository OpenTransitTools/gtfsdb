from contextlib import closing
import logging
import time
import shutil
import sys
import tempfile
from urllib import urlretrieve
import zipfile

from gtfsdb import config
from .route import Route

log = logging.getLogger(__name__)


class GTFS(object):

    def __init__(self, filename):
        self.file = filename
        self.local_file = urlretrieve(filename)[0]

    def load(self, db, **kwargs):
        '''Load GTFS into database'''
        log.debug('begin load')

        '''load known GTFS files, derived tables & lookup tables'''
        gtfs_directory = self.unzip()
        load_kwargs = dict(
            batch_size=kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE),
            gtfs_directory=gtfs_directory,
        )
        for cls in db.classes:
            cls.load(db, **load_kwargs)
        shutil.rmtree(gtfs_directory)

        '''load derived geometries, currently only written for PostgreSQL'''
        if db.is_geospatial and db.is_postgresql:
            s = ' - %s geom' % (Route.__tablename__)
            sys.stdout.write(s)
            start_seconds = time.time()
            session = db.session
            q = session.query(Route)
            for route in q:
                route.load_geometry(session)
                session.merge(route)
            session.commit()
            session.close()
            process_time = time.time() - start_seconds
            print ' (%.0f seconds)' % (process_time)
        log.debug('end load')

    def unzip(self, path=None):
        '''Unzip GTFS files from URL/directory to path.'''
        path = path if path else tempfile.mkdtemp()
        with closing(zipfile.ZipFile(self.local_file)) as z:
            z.extractall(path)
        return path
