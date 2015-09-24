from gtfsdb import Database, GTFS
import logging
import traceback
import sys
from datetime import datetime
from gtfsdb.model.metaTracking import FeedFile, GTFSExFeed

log = logging.getLogger(__name__)

def database_load(filename, db_url, file_id=None):
    try:
        db = Database(url=db_url, is_geospatial=True)
        gtfs = GTFS(filename=filename, file_id=file_id)
        gtfs.load(db)
        #gtfs.post_process(db)
        return True
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        log.error('Error processing: {} Message: {}'.format(filename,e))
        return False

def database_load_versioned(feed_meta, file_meta, db_url):
    feed_meta['date_added'] = datetime.utcfromtimestamp(feed_meta['date_added'])
    feed_meta['date_last_updated'] = datetime.utcfromtimestamp(feed_meta['date_last_updated'])
    file_meta['date_added'] = datetime.utcfromtimestamp(file_meta['date_added'])
    db = Database(url=db_url)
    session = db.get_session()
    feed = GTFSExFeed(**feed_meta)
    session.merge(feed)
    feed_file = FeedFile(dataexchange_id=feed.dataexchange_id, **file_meta)
    existing_file = session.query(FeedFile).filter_by(dataexchange_id=feed.dataexchange_id).filter_by(completed=True)\
        .order_by(FeedFile.date_added.desc()).first()

    if existing_file and existing_file.date_added >= feed_file.date_added:
        log.debug("Feed: {} already at its newest.".format(feed.dataexchange_id))
        return

    session.merge(feed_file)
    session.commit()

    try:
        database_load(filename=feed_file.file_url, db_url=db_url, file_id=feed_file.md5sum)
    except Exception, e:
        log.error("Error processing feed: {} {}".format(feed_file.filename or feed_file.file_url, e))
        return
    feed_file.completed = True
    feed_file.censio_upload_date = datetime.utcnow()
    session = db.get_session()
    session.merge(feed_file)
    session.commit()
    return

def create_shapes_geoms(db_url):
    db = Database(url=db_url, is_geospatial=True)
    gtfs = GTFS()
    gtfs.load_derived(db)
