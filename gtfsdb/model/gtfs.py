from contextlib import closing
import logging
import shutil
import tempfile
import time
from urllib import urlretrieve
import zipfile
import hashlib
from concurrent.futures import ThreadPoolExecutor

from gtfsdb import config


log = logging.getLogger(__name__)

class InputFileMismatch(Exception):
    pass

class GTFS(object):

    def __init__(self, filename=None, file_id=None):
        self.file=None
        if filename:
            self.file = filename
            log.debug("Fetching {}".format(filename))
            self.local_file = urlretrieve(filename)[0]
            log.debug("Done Fetching {}".format(filename))
            md5 = self.gen_md5(self.local_file)
            if file_id:
                if not file_id == md5:
                    raise InputFileMismatch('Input file does not match expected MD5 hash')
            self.file_id = md5




    @classmethod
    def gen_md5(cls, input_file):
        return hashlib.md5(open(input_file,'rb').read()).hexdigest()

    @staticmethod
    def bootstrab_db(db):
        for cls in db.bootstrap_classes:
            cls.load(db)

    def load(self, db, **kwargs):
        '''Load GTFS into database'''
        if not self.file:
            log.error("No Filename Specified")
            return
        start_time = time.time()
        log.debug('GTFS.load: {0}'.format(self.file))

        key_lookup = dict()

        '''load known GTFS files, derived tables & lookup tables'''
        gtfs_directory = self.unzip()
        load_kwargs = dict(
            batch_size=kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE),
            gtfs_directory=gtfs_directory,
            key_lookup=key_lookup,
            thread_pool=ThreadPoolExecutor(max_workers=kwargs.get('db_threads', config.DB_THREADS)),
            file_id=self.file_id
        )
        futures = []
        for cls in db.sorted_classes(lambda k: k.datasource == config.DATASOURCE_GTFS):
            futures += cls.load(db, **load_kwargs)
        shutil.rmtree(gtfs_directory)

        log.debug('GTFS.load: Done parsing, finishing upload')
        for future in futures:
            while future.running():
                time.sleep(0.1)
            excp = future.exception()
            if excp:
                raise excp
            future.result()

        process_time = time.time() - start_time
        log.debug('GTFS.load ({0:.0f} seconds)'.format(process_time))

    def load_derived(self, db, **kwargs):
        '''Load GTFS into database'''
        start_time = time.time()
        log.debug('GTFS.load_derived')

        load_kwargs = dict(
            batch_size=kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE),
        )
        for cls in db.sorted_classes(lambda k: k.datasource == config.DATASOURCE_DERIVED):
            cls.load(db, **load_kwargs)

        process_time = time.time() - start_time
        log.debug('GTFS.load_derived ({0:.0f} seconds)'.format(process_time))

    def post_process(self, db):
        for cls in db.sorted_classes(lambda k: k.datasource == config.DATASOURCE_GTFS):
            cls.post_process(db)
        pass


    def unzip(self, path=None):
        '''Unzip GTFS files from URL/directory to path.'''
        path = path if path else tempfile.mkdtemp()
        try:
            with closing(zipfile.ZipFile(self.local_file)) as z:
                z.extractall(path)
        except Exception, e:
            log.warning(e)
        return path
