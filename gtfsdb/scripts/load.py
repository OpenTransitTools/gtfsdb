import argparse
import time

from gtfsdb import Database, GTFS


def init_parser():
    parser = argparse.ArgumentParser(
        prog='gtfsdb-load',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'file',
        help='URL or local directory path to GTFS zip FILE',
    )
    parser.add_argument(
        '--database_url',
        default='sqlite://',
        help='DATABASE URL with appropriate privileges'
    )
    parser.add_argument(
        '--is_geospatial',
        action='store_true',
        default=False,
        help='Database IS GEOSPATIAL',
    )
    parser.add_argument(
        '--schema',
        default=None,
        help='Database SCHEMA name',
    )
    args = parser.parse_args()
    return args


def main():
    # process command line args
    args = init_parser()
    # create database
    db = Database(args.database_url, args.schema, args.is_geospatial)
    db.create()
    # load GTFS into database
    gtfs = GTFS(args.file)
    gtfs.load(db)


if __name__ == '__main__':
    start_seconds = time.time()
    start_time = time.localtime()
    print time.strftime('begin time: %H:%M:%S', start_time)
    main()
    end_time = time.localtime()
    print time.strftime('end time: %H:%M:%S', end_time)
    process_time = time.time() - start_seconds
    print 'processing time: %.0f seconds' %(process_time)
