import codecs
from StringIO import StringIO
import tempfile
from time import time
from urllib import urlopen
import zipfile


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


def unzip_gtfs(url_to_zip):
    """Unzip known GTFS files from URL/directory to temp directory."""
    start_time = time()
    temp_directory = tempfile.mkdtemp()
    file_handle = urlopen(url_to_zip)
    zipdata = StringIO(file_handle.read())
    file_handle.close()
    zip = zipfile.ZipFile(zipdata)
    files = list(set(zip.namelist()).intersection(set(model.files)))
    zip.extractall(temp_directory, files)
    processing_time = time() - start_time
    print ' %s (%.0f seconds)' %(url_to_zip, processing_time)
    return temp_directory
