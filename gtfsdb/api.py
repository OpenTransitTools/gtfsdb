from gtfsdb import Database, GTFS
from gtfsdb.model.feed_info import DataexchangeInfo
import logging
import datetime

log = logging.getLogger(__name__)

'''
{
    'dataexchange_id': "",
    'file_url': "URL",
    'file_name': "Filename",
    'file_checksum' : "MD5Has"
    'date_added': 1213154234.0
}
'''


def database_load_versioned(source_meta, db_url, force=False):
    db = Database(url=db_url, is_geospatial=True)
    exchange_record = DataexchangeInfo(
        agency_id=source_meta['dataexchange_id'], **source_meta)
    if force or DataexchangeInfo.overwrite(db, exchange_record):
        database_load(source_meta['file_url'], db_url=db_url)
        exchange_record.completed=True
        exchange_record.completed_on = datetime.datetime.utcnow()
        session = db.get_session()
        session.merge(exchange_record)
        session.commit()
    else:
        rec = db.session.query(DataexchangeInfo).get(source_meta['dataexchange_id'])
        logging.debug("Feed '{}' already uploaded on: {}".format(rec.dataexchange_id, rec.completed_on))


def database_load(filename, db_url):
    db = Database(url=db_url, is_geospatial=True)
    gtfs = GTFS(filename=filename)
    gtfs.load(db)
