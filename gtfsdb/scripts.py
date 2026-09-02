from __future__ import print_function

import argparse

from gtfsdb import config
from gtfsdb import util
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
        current_tables_all=args.current_tables_all,
        current_tables_rid=args.current_tables_route_id,

        # less used params
        do_postprocess=not args.ignore_postprocess,
        ignore_blocks=args.ignore_blocks,
        tables=args.tables,
        batch_size=args.batch_size
    )
    return kwargs


def make_args(prog_name='gtfsdb-load', do_parse=True, def_db=config.DEFAULT_DATABASE_URL, def_schema=config.DEFAULT_SCHEMA):
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
    parser.add_argument('--database_url', '-d', default=def_db,
                        help='DATABASE URL with appropriate privileges')
    parser.add_argument('--is_geospatial', '-g', action='store_true',
                        default=config.DEFAULT_IS_GEOSPATIAL,
                        help='Database supports GEOSPATIAL functions')
    parser.add_argument('--feed_id', '-f', default=None,
                        help='GTFS Feed ID (often upper case version of schema name)')
    parser.add_argument('--schema', '-s', default=def_schema, help='Database SCHEMA name')
    parser.add_argument('--tables', choices=tables, default=None, nargs='*',
                        help='Limited list of TABLES to load, if blank, load all tables')
    parser.add_argument('--create', '-c', action="store_true",
                        help='create new db tables (note: not currently used in gtfsdb, which always creates tables)')
    parser.add_argument('--print', '-p', action="store_true",
                        help='print results from some sql query or data transform to cmdline')
    parser.add_argument('--ignore_stop_codes', '-nsc', default=False, action='store_true',
                        help="no public stop codes or ids should be used, so don't publish stop codes to downstream systems")
    parser.add_argument('--ignore_postprocess', '-np', default=False, action='store_true',
                        help="don't run any postprocess model routines (will leave some tables empty ... but will load raw gtfs data)")
    parser.add_argument('--ignore_blocks', '-nb', default=False, action='store_true',
                        help="don't bother populating the derived block table")

    parser.add_argument('--current_tables', '-ct', default=False, action='store_true',
                        help="create tables that represent 'current' service (e.g., views)")
    parser.add_argument('--current_tables_all', '-cta', default=False, action='store_true',
                        help="load current tables with everything in the load tables (don't bother calculating current service)")
    parser.add_argument('--current_tables_route_id', '-ctrid', '-rid', default=None, nargs='*',
                        help="strip these characters from the end of a route id")
    parser.add_argument('--current_start_date', '-csd', default=None, help="optional start date for the current tables")
    parser.add_argument('--current_end_date',   '-ced', default=None, help="optional end date for the current tables")
    parser.add_argument('--current_start_dow', '-sdow', default="Sunday", help="dow for start of the current calculation")
    parser.add_argument('--current_end_dow',   '-edow', default="Saturday", help="dow for ending the current calculation")

    if do_parse:
        args = parser.parse_args()
        kwargs = make_kwargs(args)

        # set the feed_id to the uppercase schema name by default
        if kwargs.get('feed_id') is None and kwargs.get('schema') is not None:
            kwargs['feed_id'] = kwargs.get('schema').upper()
            args.feed_id = kwargs.get('schema').upper()
    else:
        args = parser
        kwargs = None

    return args, kwargs


def gtfsdb_load():
    args, kwargs = make_args()
    database_load(args.file, **kwargs)


def route_stop_load():
    """
    written as a test / debug method for RS table loader
    """
    from gtfsdb import Database, RouteStop
    kwargs = make_args()[1]
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
    #import pdb; pdb.set_trace()
    args, kwargs = make_args('gtfsdb-current-load')
    if args.current_start_date and args.current_end_date:
        from_date,to_date = util.check_date_range(args.current_start_date, args.current_end_date)
    else:
        d = args.current_start_date or args.file
        in_date,from_date,to_date = util.get_date_range(d, args.current_start_dow, args.current_end_dow)

    kwargs['from_date'] = from_date
    kwargs['to_date'] = to_date
    print(f"range: {kwargs.get('from_date')} to {kwargs.get('to_date')}")
    current_tables_load(**kwargs)


def db_connect_tester():
    """
    simple routine to connect to an existing database and list a few stops
    bin/connect-tester --database_url sqlite:///gtfs.db _no_gtfs_zip_needed_
    """
    from gtfsdb import Database, Stop, Route, StopTime
    args, kwargs = make_args('connect-tester')
    db = Database(**kwargs)
    for s in db.session.query(Stop).limit(2):
        print(s.stop_name)
    for r in db.session.query(Route).limit(2):
        print(r.route_name)
    stop_times = StopTime.get_departure_schedule(db.session, stop_id='11411')
    for st in stop_times:
        print(st.get_direction_name())
        break
