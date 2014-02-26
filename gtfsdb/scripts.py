import argparse
from gtfsdb.api import database_load


def gtfsdb_load():
    parser = argparse.ArgumentParser(prog='gtfsdb-load',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='URL or local path to GTFS zip FILE')
    parser.add_argument('--batch_size', default=10000,
        help='BATCH SIZE to use for memory management')
    parser.add_argument('--database_url', default='sqlite://',
        help='DATABASE URL with appropriate privileges')
    parser.add_argument('--is_geospatial', action='store_true', default=False,
        help='Database supports GEOSPATIAL functions')
    parser.add_argument('--schema', default=None, help='Database SCHEMA name')
    args = parser.parse_args()

    database_load(
        args.file, args.database_url, args.schema, args.is_geospatial)
