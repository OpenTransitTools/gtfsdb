from gtfsdb import Database, GTFS
import logging
import traceback
import sys

import getpass

from datetime import datetime
from gtfsdb.model.metaTracking import FeedFile, GTFSExAgency
from gtfsdb.import_api.gtfs_exchange import GTFSExchange
from gtfsdb.model.shape import Shape, ShapeGeom
from sqlalchemy import distinct
import os

log = logging.getLogger(__name__)

def database_load(filename, db_url, **kwargs):
    db = Database(url=db_url, is_geospatial=True)
    gtfs = GTFS(filename=filename, file_id=kwargs.get('file_id'))
    gtfs.load(db)
    #gtfs.post_process(db)


def load_external_agencies(session, agency_meta):
    session.merge(GTFSExAgency(**agency_meta))
    session.commit()


def database_load_versioned(feed_file, db_url, **kwargs):
    db = Database(url=db_url)
    session = db.get_session()
    existing_file = session.query(FeedFile).get(feed_file.md5sum)

    if existing_file and existing_file.completed:
        log.debug("FeedFile: {} already at its newest.".format(feed_file.file_url))
        return

    session.merge(feed_file)
    session.commit()

    try:
        database_load(filename=feed_file.file_url, db_url=db_url, file_id=feed_file.md5sum, **kwargs)
        feed_file.completed = True
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        log.error('Error processing: {} Message: {}'.format(feed_file.file_url,e))
    finally:
        feed_file.censio_upload_date = datetime.utcnow()
        session = db.get_session()
        session.merge(feed_file)
        session.commit()

def create_shapes_geom(db_url, shape_id):
    db = Database(url=db_url, is_geospatial=True)
    session = db.get_session()
    session.merge(ShapeGeom.create_shape_geom(shape_id, session))
    session.commit()


def get_gtfs_feeds(session, dataexchangeid_list=[]):
    gtfs_api = GTFSExchange()
    feeds = []
    for feed in gtfs_api.get_gtfs_agencies(True):
        if len(dataexchangeid_list) > 0:
            if feed['dataexchange_id'] not in dataexchangeid_list:
                continue
        details = gtfs_api.get_gtfs_agency_details(feed)['agency']
        load_external_agencies(session, details)
        feeds.append(FeedFile(**gtfs_api.get_most_recent_file(feed)['file']))
    return feeds

def get_feeds_from_directory(directory):
    file_list = []
    upload_date = datetime.utcnow()
    user = format('censio-{}'.format(getpass.getuser()))
    def create_feed_obj(f_path):
        f_path = os.path.abspath(f_path)
        md5_sum = GTFS.gen_md5(f_path)
        return FeedFile(md5sum=md5_sum, date_added=upload_date, uploaded_by_user=user,
                        file_url=f_path, description='Manual Upload')

    if directory.endswith(".zip"):
        return [create_feed_obj(directory)]
    for root, dirs, files in os.walk(directory):
        for f in files:
            if ".zip" in f:
                file_list.append(create_feed_obj(os.path.join(root, f)))
    return file_list
