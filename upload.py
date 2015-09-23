__author__ = 'rhunter'

import argparse
from sqlalchemy.exc import IntegrityError
from joblib import Parallel, delayed
import json
import os

from gtfsdb.model.db import Database
from gtfsdb.model.metaTracking import Meta
from gtfsdb.model.gtfs import GTFS
from gtfsdb.api import database_load
from gtfsdb.import_api.custom import gtfs_source_list
from gtfsdb.import_api.gtfs_exchange import GTFSExchange
import datetime

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
    meta = Meta(file_name=source)
    db.session.add(meta)
    db.session.commit()
    database_load(source, database)
    meta.completed = True
    meta.upload_date = datetime.datetime.utcnow()
    db.session.commit()

def main(database, parallel=0):
    db = Database(url=database, is_geospatial=True)
    db.create()
    #try:
    #    GTFS.bootstrab_db(db)
    #except IntegrityError:
    #    pass

    sources = []
    sources += ['data/sample-feed.zip']
    #sources += gtfs_dump()
    #sources += [zip_sources()[0]]
    #sources += internal_file()
    #sources += gtfs_ex_sources()
    #sources += gtfs_ex_api()

    if parallel:
        concurrent_run(sources, database, parallel)
    else:
        serial_run(sources, database)


def serial_run(sources, database):
    for source in sources:
        tag_meta(source, database)


def concurrent_run(sources, database, num_jobs):
    Parallel(n_jobs=int(num_jobs))(delayed(tag_meta)(source, database) for source in sources)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', help='the database url')
    parser.add_argument('-p', '--parallel')
    args = parser.parse_args()
    main(database=args.database, parallel=args.parallel)


