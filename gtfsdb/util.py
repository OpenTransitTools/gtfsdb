import codecs
from StringIO import StringIO
import sys
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
        return self.reader.next().encode('utf-8')


def unzip_gtfs(url_to_zip):
    """Unzip GTFS files from URL/directory to temp directory."""
    sys.stdout.write('Processing {0}'.format(url_to_zip))
    start_time = time()
    temp_directory = tempfile.mkdtemp()
    file_handle = urlopen(url_to_zip)
    zipdata = StringIO(file_handle.read())
    file_handle.close()
    zip = zipfile.ZipFile(zipdata)
    zip.extractall(temp_directory)
    process_time = time() - start_time
    sys.stdout.write(' ({0:.0f} seconds)\n'.format(process_time))
    return temp_directory
