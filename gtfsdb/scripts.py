from __future__ import print_function

import argparse

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.api import database_load


def make_kwargs(args):
    # see below...
    kwargs = dict(
        # common cmd line items
        url=args.database_url,
        schema=args.schema,
        is_geospatial=args.is_geospatial,
        current_tables=args.current_tables,

        # less used params
        do_postprocess=not args.ignore_postprocess,
        ignore_blocks=args.ignore_blocks,
        tables=args.tables,
        batch_size=args.batch_size
    )
    return kwargs


def get_args(prog_name='gtfsdb-load', do_parse=True):
    """
    database load command-line arg parser and help util...
    """
    tables = sorted([t.name for t in Base.metadata.sorted_tables])
    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('file', help='URL or local path to GTFS zip FILE')
    parser.add_argument('--batch_size', '-b', type=int, default=config.DEFAULT_BATCH_SIZE,
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
    parser.add_argument('--create', '-c', action="store_true",
                        help='create new db tables (note: not currently used in gtfsdb, which always creates tables)')
    parser.add_argument('--current_tables', '-ct', default=False, action='store_true',
                        help="create tables that represent 'current' service (e.g., views)")
    parser.add_argument('--ignore_postprocess', '-np', default=False, action='store_true',
                        help="don't run any postprocess model routines (will leave some tables empty ... but will load raw gtfs data)")
    parser.add_argument('--ignore_blocks', '-nb', default=False, action='store_true',
                        help="don't bother populating the derrived block table")
    if do_parse:
        args = parser.parse_args()
        kwargs = make_kwargs(args)
    else:
        args = parser
        kwargs = None

    return args, kwargs


def gtfsdb_load():
    args, kwargs = get_args()
    database_load(args.file, **kwargs)


def route_stop_load():
    """
    written as a test / debug method for RS table loader
    """
    from gtfsdb import Database, RouteStop
    kwargs = get_args()[1]
    db = Database(**kwargs)
    RouteStop.load(db, **kwargs)


def current_tables_load(**kwargs):
    """
    current table loader
    """
    from gtfsdb import Database, CurrentRoutes, CurrentStops, CurrentRouteStops
    db = Database(**kwargs)
    for cls in [CurrentRoutes, CurrentRouteStops, CurrentStops]:
        db.create_table(cls)
        cls.post_process(db, **kwargs)


def current_tables_cmdline():
    kwargs = get_args('gtfsdb-current-load')[1]
    current_tables_load(**kwargs)


def db_connect_tester():
    """
    simple routine to connect to an existing database and list a few stops
    bin/connect-tester --database_url sqlite:///gtfs.db _no_gtfs_zip_needed_
    """
    from gtfsdb import Database, Stop, Route, StopTime
    args, kwargs = get_args('connect-tester')
    db = Database(**kwargs)
    for s in db.session.query(Stop).limit(2):
        print(s.stop_name)
    for r in db.session.query(Route).limit(2):
        print(r.route_name)
    stop_times = StopTime.get_departure_schedule(db.session, stop_id='11411')
    for st in stop_times:
        print(st.get_direction_name())
        break
