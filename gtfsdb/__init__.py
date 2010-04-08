__import__('pkg_resources').declare_namespace(__name__)

from gtfsdb.model.agency import Agency
from gtfsdb.model.calendar import Calendar, CalendarDate, UniversalCalendar
from gtfsdb.model.fare import FareAttribute, FareRule
from gtfsdb.model.frequency import Frequency
from gtfsdb.model.route import Route, RouteType
from gtfsdb.model.shape import Pattern, Shape
from gtfsdb.model.stop import Stop
from gtfsdb.model.stop_time import StopTime
from gtfsdb.model.transfer import Transfer
from gtfsdb.model.trip import Trip

from StringIO import StringIO
import tempfile
from time import time
from urllib import urlopen
import zipfile
from zipfile import ZipFile

#
# from py-2.6 - rewritten locally for 2.6 compatibility
#
def extractall(zip, path=None, members=None, pwd=None):
        if members is None:
            members = self.namelist()
        for zipinfo in members:
            p = zipinfo
            if path != None:
                p = path + "/" + zipinfo
            bs = zip.read(zipinfo)
            fp = open(p, 'w')
            fp.write(bs)
            fp.close()


def unzip_gtfs(url_to_zip):
    """Unzip known GTFS files from URL/directory to temp directory."""
    start_time = time()
    temp_directory = tempfile.mkdtemp()
    file_handle = urlopen(url_to_zip)
    zipdata = StringIO(file_handle.read())
    file_handle.close()
    zip = zipfile.ZipFile(zipdata)
    files = list(set(zip.namelist()).intersection(set(model.files)))
    extractall(zip, temp_directory, files)
    processing_time = time() - start_time
    print ' %s (%.0f seconds)' %(url_to_zip, processing_time)
    return temp_directory
