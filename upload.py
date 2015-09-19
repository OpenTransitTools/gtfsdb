__author__ = 'rhunter'

import argparse
from sqlalchemy.exc import IntegrityError
from joblib import Parallel, delayed

from gtfsdb.model.db import Database
from gtfsdb.model.gtfs import GTFS
from gtfsdb.api import database_load


def main(database, parallel=False):
    db = Database(url=database, is_geospatial=True)
    db.create()
    try:
        GTFS.bootstrab_db(db)
    except IntegrityError:
        pass

    sources = ['data/action_20150129_0101.zip',
               'data/abq-ride_20150802_0107.zip']

    if parallel:
        concurrent_run(sources, database)
    else:
        serial_run(sources, database)


def serial_run(sources, database):
    for source in sources:
        database_load(source, database)


def concurrent_run(sources, database):
    Parallel(n_jobs=36)(delayed(database_load)(source, database) for source in sources)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', help='the database url')
    parser.add_argument('-p', '--parallel', action='store_true')
    args = parser.parse_args()
    main(database=args.database, parallel=args.parallel)


