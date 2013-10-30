import argparse
import logging

from gtfsdb import Database, GTFS


log = logging.getLogger(__name__)


def load(filename, database_url='sqlite://', schema=None, is_geospatial=False):
    '''Basic API to load a GTFS zip file'''
    db = Database(database_url, schema, is_geospatial)
    db.create()
    gtfs = GTFS(filename)
    gtfs.load(db)


def main():
    parser = argparse.ArgumentParser(prog='gtfsdb-load',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='URL or local path to GTFS zip FILE')
    parser.add_argument('--database_url', default='sqlite://',
        help='DATABASE URL with appropriate privileges')
    parser.add_argument('--is_geospatial', action='store_true', default=False,
        help='Database IS GEOSPATIAL')
    parser.add_argument('--schema', default=None, help='Database SCHEMA name')
    args = parser.parse_args()

    load(args.file, args.database_url, args.schema, args.is_geospatial)


if __name__ == '__main__':
    main()
