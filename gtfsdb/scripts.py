import argparse

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.api import database_load


def gtfsdb_load():
    tables = sorted([t.name for t in Base.metadata.sorted_tables])
    parser = argparse.ArgumentParser(prog='gtfsdb-load',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='URL or local path to GTFS zip FILE')
    parser.add_argument('--batch_size', default=config.DEFAULT_BATCH_SIZE,
        help='BATCH SIZE to use for memory management')
    parser.add_argument('--database_url', default=config.DEFAULT_DATABASE_URL,
        help='DATABASE URL with appropriate privileges')
    parser.add_argument('--is_geospatial', action='store_true',
        default=config.DEFAULT_IS_GEOSPATIAL,
        help='Database supports GEOSPATIAL functions')
    parser.add_argument('--schema', default=config.DEFAULT_SCHEMA,
        help='Database SCHEMA name')
    parser.add_argument('--tables', choices=tables, default=None, nargs='*',
        help='Limited list of TABLES to load, if blank, load all tables')
    args = parser.parse_args()

    kwargs = dict(
        batch_size=args.batch_size,
        schema=args.schema,
        is_geospatial=args.is_geospatial,
        tables=args.tables,
        url=args.database_url,
    )
    database_load(args.file, **kwargs)
