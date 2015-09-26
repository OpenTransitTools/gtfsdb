__author__ = 'rhunter'

import argparse
from joblib import Parallel, delayed
import json
import os

from gtfsdb.model.db import Database
from gtfsdb.api import database_load, database_load_versioned, load_external_agencies
from gtfsdb.import_api.custom import gtfs_source_list
from gtfsdb.import_api.gtfs_exchange import GTFSExchange
from gtfsdb.model.metaTracking import FeedFile
import datetime

from gtfsdb.model.agency import Agency

#def failed(session):
#    return [ f.file_name for f in session.query(Meta).filter_by(completed=False).filter_by(upload_date=None).all()]

def zip_sources():
    return ['data/action_20150129_0101.zip', 'data/abq-ride_20150802_0107.zip']

def gtfs_dump():
    return [ datafile['file_url'] for datafile in gtfs_source_list('data/file_list.pkl') ]

def gtfs_ex_sources():
    return json.load(open('ex_files.json', 'r'))['file_list']

def gtfs_ex_api():
    file_list = []
    gtfs_api = GTFSExchange()
    for agency in gtfs_api.get_gtfs_agencies(official_only=False):
        details = gtfs_api.get_gtfs_agency_details(agency)
        file = gtfs_api.get_most_recent_file(agency)
        if file:
            file_list.append(file['file']['file_url'])
    return file_list

def internal_file():
    file_list = []
    for root, dirs, files in os.walk('internal_data/'):
        for f in files:
            if ".zip" in f:
                file_list.append(os.path.join(root, f))
    return file_list


def tag_meta(source, database):
    db = Database(url=database)
    meta = db.session.query(Meta).filter_by(file_name=source).first()
    if not meta:
        meta = Meta(file_name=source)
        db.session.add(meta)
        db.session.commit()
    meta.completed = database_load(source, database)
    meta.upload_date = datetime.datetime.utcnow()
    db.session.commit()


def get_gtfs_feeds(session):
    gtfs_api = GTFSExchange()
    feeds = []
    for feed in gtfs_api.get_gtfs_agencies(True):
        if not feed['country'] == 'United States':
            continue
        details = gtfs_api.get_gtfs_agency_details(feed)['agency']
        load_external_agencies(session, details)
        feeds.append(FeedFile(**gtfs_api.get_most_recent_file(feed)['file']))
    return feeds

def main(database, parallel=0):

    db = Database(url=database, is_geospatial=True)
    db.create()

    feeds = set(get_gtfs_feeds(db.get_session()))

    db.drop_indexes()

    if parallel:
        concurrent_run(feeds, database, parallel)
    else:
        serial_run(feeds, database)

    db.create_indexes()

def serial_run(sources, database):
    for source in sources:
        database_load_versioned(db_url=database, feed_file=source)


def concurrent_run(sources, database, num_jobs):
    Parallel(n_jobs=int(num_jobs))(delayed(database_load_versioned)(db_url=database, feed_file=source) for source in sources)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', help='the database url')
    parser.add_argument('-p', '--parallel')
    args = parser.parse_args()
    main(database=args.database, parallel=args.parallel)


