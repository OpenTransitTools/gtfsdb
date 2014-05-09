import argparse

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.api import database_load

def gtfsdb_load():
    kwargs = get_args()
    db = database_load(args.file, **kwargs)

def route_stop_load():
    ''' written as a test / debug method for RS table loader '''
    from gtfsdb import Database, RouteStop
    kwargs = get_args()
    db = Database(**kwargs)
    #import pdb; pdb.set_trace()
    RouteStop.load(db, **kwargs)

def get_args():
    ''' database load command-line arg parser and help util...
    '''
    tables = sorted([t.name for t in Base.metadata.sorted_tables])
    parser = argparse.ArgumentParser(prog='gtfsdb-load',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='URL or local path to GTFS zip FILE')
    parser.add_argument('--batch_size', default=config.DEFAULT_BATCH_SIZE,
        help='BATCH SIZE to use for memory management')
    parser.add_argument('--database_url', '-d', default=config.DEFAULT_DATABASE_URL,
        help='DATABASE URL with appropriate privileges')
    parser.add_argument('--is_geospatial', '-g', action='store_true',
        default=config.DEFAULT_IS_GEOSPATIAL,
        help='Database supports GEOSPATIAL functions')
    parser.add_argument('--schema', '-s', default=config.DEFAULT_SCHEMA,
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
    return kwargs
