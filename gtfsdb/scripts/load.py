from gtfsdb import (
    Agency,
    Calendar,
    CalendarDate,
    FareAttribute,
    FareRule,
    Frequency,
    model,
    Pattern,
    Route,
    RouteType,
    Shape,
    Stop,
    StopTime,
    Transfer,
    Trip,
    UniversalCalendar,
    unzip_gtfs,
)
from optparse import OptionParser
import pkg_resources
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import ConfigParser


def get_default_config(options):
    path = pkg_resources.resource_filename('gtfsdb', 'data')
    filename = '%s/default.cfg' %(path)
    config = ConfigParser.ConfigParser()
    config.read(filename)

    section = 'options'
    options.create = config.getboolean(section, 'create')
    options.database = config.get(section, 'database')
    options.filename = config.get(section, 'filename')
    options.geospatial = config.getboolean(section, 'geospatial')
    if config.has_option(section, 'schema'):
        options.schema = config.get(section, 'schema')
    else:
        options.schema = None
    
    return options


def init_parser():
    parser = OptionParser()
    parser.set_defaults(create=False, schema=None, geospatial=False)
    parser.add_option(
        "-c", "--create", action="store_true", dest="create",
        help="Create database tables"
    )
    parser.add_option(
        "-d", "--database", dest="database",
        help="Database connection string for engine"
    )
    parser.add_option(
        "-f", "--file", dest="filename",
        help="URL or local directory path to GTFS zip file"
    )
    parser.add_option(
        "-g", "--geom", action="store_true", dest="geospatial",
        help="Indicate that database is spatially enabled"
    )
    parser.add_option(
        "-s", "--schema", dest="schema",
        help="Optional database schema name"
    )
    (options, args) = parser.parse_args()
    if options.database is None:
        options = get_default_config(options)
    return options


def main():
    options = init_parser()
    engine = create_engine(options.database)
    model.init(options)
    if options.create:
        model.DeclarativeBase.metadata.drop_all(bind=engine)
        model.DeclarativeBase.metadata.create_all(bind=engine)
    gtfs_directory = unzip_gtfs(options.filename)
    data_directory = pkg_resources.resource_filename('gtfsdb', 'data')

    # load lookup tables first
    RouteType.load(engine, data_directory, False)

    # load GTFS data files & transform/derive additional data
    # due to foreign key constraints these files need to be loaded in the appropriate order
    Agency.load(engine, gtfs_directory)
    Calendar.load(engine, gtfs_directory)
    CalendarDate.load(engine, gtfs_directory)
    Route.load(engine, gtfs_directory)
    Stop.load(engine, gtfs_directory)
    Transfer.load(engine, gtfs_directory)
    Shape.load(engine, gtfs_directory)
    Pattern.load(engine)
    Trip.load(engine, gtfs_directory)
    StopTime.load(engine, gtfs_directory)
    Frequency.load(engine, gtfs_directory)
    FareAttribute.load(engine, gtfs_directory)
    FareRule.load(engine, gtfs_directory)
    shutil.rmtree(gtfs_directory)
    UniversalCalendar.load(engine)

    # load derived geometries
    # currently only written for postgresql
    dialect_name = engine.url.get_dialect().name
    if options.geospatial and dialect_name == 'postgres':
        Session = sessionmaker(bind=engine)
        session = Session()
        q = session.query(Route)
        for route in q:
            route.load_geometry(session)
            session.merge(route)
        session.commit()
        session.close()

if __name__ == '__main__':
    start_seconds = time.time()
    start_time = time.localtime()
    print time.strftime('begin time: %H:%M:%S', start_time)
    main()
    end_time = time.localtime()
    print time.strftime('end time: %H:%M:%S', end_time)
    process_time = time.time() - start_seconds
    print 'processing time: %.0f seconds' %(process_time)
