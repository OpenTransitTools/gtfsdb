from contextlib import closing
import logging
import shutil
import tempfile
import time
from urllib import urlretrieve
import zipfile
import uuid

from gtfsdb import config
from .route import Route


log = logging.getLogger(__name__)


class GTFS(object):

    def __init__(self, filename, unique_id=None):
        self.file = filename
        log.debug("Fetching {}".format(filename))
        self.local_file = urlretrieve(filename)[0]
        log.debug("Done Fetching {}".format(filename))
        self.unique_id = unique_id if unique_id else str(uuid.uuid4())

    @staticmethod
    def bootstrab_db(db):
        for cls in db.bootstrap_classes:
            cls.load(db)

    def load(self, db, **kwargs):
        '''Load GTFS into database'''
        start_time = time.time()
        log.debug('GTFS.load: {0}'.format(self.file))

        '''load known GTFS files, derived tables & lookup tables'''
        gtfs_directory = self.unzip()
        load_kwargs = dict(
            batch_size=kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE),
            gtfs_directory=gtfs_directory,
        )
        for cls in db.sorted_classes:
            cls.unique_id = self.unique_id
            cls.load(db, **load_kwargs)
        shutil.rmtree(gtfs_directory)


        '''load route geometries derived from shapes.txt'''
        if Route in db.classes:
            Route.load_geoms(db)

        for cls in db.sorted_classes:
            cls.post_process(db)

        process_time = time.time() - start_time
        log.debug('GTFS.load ({0:.0f} seconds)'.format(process_time))

    def unzip(self, path=None):
        '''Unzip GTFS files from URL/directory to path.'''
        path = path if path else tempfile.mkdtemp()
        try:
            with closing(zipfile.ZipFile(self.local_file)) as z:
                z.extractall(path)
        except Exception, e:
            log.warning(e)
        return path

    def delete_agency_data(self, db, agency_id):
        session = db.get_session()
        def delete(cls):
            session.query(cls).filter_by(agency_id=agency_id).delete()
        for cls in reversed(db.sorted_classes):
            delete(cls)
        for cls in set(db.classes)-set(db.sorted_classes):
            delete(cls)
        session.commit()
        session.close()
