from contextlib import closing
import logging
import shutil
import tempfile
import time
try:
    from urllib import urlretrieve  # Python 2
except ImportError:
    from urllib.request import urlretrieve  # Python 3
import zipfile

from gtfsdb import config
from .route import Route

log = logging.getLogger(__name__)


class GTFS(object):

    def __init__(self, filename):
        # import pdb; pdb.set_trace()
        # TODO: replace old/clunky urlretrieve() with requests.get
        self.file = filename
        try:
            self.local_file = urlretrieve(filename)[0]
        except Exception:
            try:
                self.local_file = urlretrieve("file:///" + filename)[0]
            except Exception:
                self.local_file = filename

    def load(self, db, **kwargs):
        """
        Load GTFS into database
        """
        # import pdb; pdb.set_trace()
        start_time = time.time()
        log.debug('GTFS.load: {0}'.format(self.file))

        # step 1: load .txt files from GTFS.zip, as well as derived tables & lookup tables from gtfsdb/data
        gtfs_directory = self.unzip()
        kwargs['gtfs_directory'] = gtfs_directory
        db.load_tables(**kwargs)
        shutil.rmtree(gtfs_directory)

        # step 2: call post process routines...
        db.postprocess_tables(**kwargs)

        # step 3: finish
        process_time = time.time() - start_time
        log.debug('GTFS.load ({0:.0f} seconds)'.format(process_time))

    def unzip(self, path=None):
        """
        Unzip GTFS files from URL/directory to path.
        """
        path = path if path else tempfile.mkdtemp()
        try:
            with closing(zipfile.ZipFile(self.local_file)) as z:
                z.extractall(path)
        except Exception as e:
            log.warning(e)
        return path
