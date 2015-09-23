from ConfigParser import ConfigParser
import logging.config
import os
from pkg_resources import resource_filename  # @UnresolvedImport


'''Parse configuration file and setup logging'''
config = ConfigParser()
ini_file = os.path.join(resource_filename('gtfsdb', 'configs'), 'app.ini')
config.read(ini_file)
if config.has_section('loggers'):
    logging.config.fileConfig(ini_file, disable_existing_loggers=False)

DB_ATTEMPTS = 4
'''Application defaults'''
DEFAULT_BATCH_SIZE = 100000
DEFAULT_DATABASE_URL = 'sqlite://'
DEFAULT_IS_GEOSPATIAL = False
DEFAULT_SCHEMA = 'public'

'''Data source constants'''
DATASOURCE_DERIVED = 3
DATASOURCE_GTFS = 1
DATASOURCE_LOOKUP = 2

'''Geometry constants'''
SRID = 900913

'''Order list of class names, used for creating & populating tables'''

INITIAL_LOAD_CLASS = [
    'RouteType',
    'RouteFilter'
]

SORTED_CLASS_NAMES = [
    'FeedInfo',
    'Agency',
    'Calendar',
    'CalendarDate',
    'Route',
    'RouteDirection',
    'Stop',
    'StopFeature',
    'Transfer',
    'Shape',
    'ShapeGeom',
    'Trip',
    'StopTime',
    'RouteStop',
    'Frequency',
    'FareAttribute',
    'FareRule',
    'UniversalCalendar'
]
