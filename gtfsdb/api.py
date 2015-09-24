from gtfsdb import Database, GTFS
import logging
import traceback
import sys

log = logging.getLogger(__name__)

def database_load(filename, db_url):
    try:
        db = Database(url=db_url, is_geospatial=True)
        gtfs = GTFS(filename=filename)
        gtfs.load(db)
        #gtfs.post_process(db)
        return True
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        log.error('Error processing: {} Message: {}'.format(filename,e))
        return False

def create_shapes_geoms(db_url):
    db = Database(url=db_url, is_geospatial=True)
    gtfs = GTFS()
    gtfs.load_derived(db)
