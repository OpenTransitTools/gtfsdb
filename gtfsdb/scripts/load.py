import csv
from gtfsdb import *
from optparse import OptionParser
import os
import pkg_resources
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import time
import ConfigParser


def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


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


def load_file(engine, directory, cls, validate=True):
    records = []
    file_path = '%s/%s' %(directory, cls.get_filename())
    if os.path.exists(file_path):
        start_time = time.time()
        file = open(file_path)
        reader =  csv.DictReader(file)
        if validate:
            cls.validate(reader.fieldnames)
        s = ' %s ' %(cls.get_filename())
        sys.stdout.write(s)
        table = cls.__table__
        engine.execute(table.delete())
        i = 0
        for row in reader:
            records.append(cls.make_record(row))
            i += 1
            # commit every 10,000 records to the database to manage memory usage
            if i >= 10000:
                engine.execute(table.insert(), records)
                sys.stdout.write('*')
                records = []
                i = 0
        if len(records) > 0:
            engine.execute(table.insert(), records)
        file.close()
        processing_time = time.time() - start_time
        print ' (%.0f seconds)' %(processing_time)


def main():
    options = init_parser()
    engine = create_engine(options.database)
    model.init(options)
    if options.create:
        model.DeclarativeBase.metadata.drop_all(bind=engine)
        model.DeclarativeBase.metadata.create_all(bind=engine)
    gtfs_directory = unzip_gtfs(options.filename)
    data_directory = pkg_resources.resource_filename('gtfsdb', 'data')
    # load GTFS data files, due to foreign key constraints
    # these files need to be loaded in the appropriate order
    load_file(engine, gtfs_directory, Agency)
    load_file(engine, gtfs_directory, Calendar)
    load_file(engine, gtfs_directory, CalendarDate)
    load_file(engine, data_directory, RouteType, False)
    load_file(engine, gtfs_directory, Route)
    load_file(engine, gtfs_directory, Stop)
    load_file(engine, gtfs_directory, Transfer)
    load_file(engine, gtfs_directory, Shape)
    load_file(engine, gtfs_directory, Trip)
    load_file(engine, gtfs_directory, StopTime)
    load_file(engine, gtfs_directory, Frequency)
    load_file(engine, gtfs_directory, FareAttribute)
    load_file(engine, gtfs_directory, FareRule)
    shutil.rmtree(gtfs_directory)


if __name__ == '__main__':
    start_seconds = time.time()
    start_time = time.localtime()
    print time.strftime('begin time: %H:%M:%S', start_time)
    main()
    end_time = time.localtime()
    print time.strftime('end time: %H:%M:%S', end_time)
    process_time = time.time() - start_seconds
    print 'processing time: %.0f seconds' %(process_time)
