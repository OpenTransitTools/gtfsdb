from contextlib import closing
import logging
import shutil
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
        log.debug('begin GTFS.load')

        '''load known GTFS files, derived tables & lookup tables'''
        gtfs_directory = self.unzip()
        load_kwargs = dict(
            batch_size=kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE),
            gtfs_directory=gtfs_directory,
        )
        for cls in db.sorted_classes:
            cls.load(db, **load_kwargs)
        shutil.rmtree(gtfs_directory)

        '''load route geometries derived from shapes.txt'''
        Route.load_geoms(db)
        log.debug('end GTFS.load')

    def unzip(self, path=None):
        '''Unzip GTFS files from URL/directory to path.'''
        path = path if path else tempfile.mkdtemp()
        with closing(zipfile.ZipFile(self.local_file)) as z:
            z.extractall(path)
        return path
