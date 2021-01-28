try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import os
import logging.config
from pkg_resources import resource_filename  # @UnresolvedImport


""" parse configuration file and setup logging """
config = ConfigParser()
ini_file = os.path.join(resource_filename('gtfsdb', 'configs'), 'app.ini')
config.read(ini_file)
if config.has_section('loggers'):
    logging.config.fileConfig(ini_file, disable_existing_loggers=False)


""" application defaults """
DEFAULT_BATCH_SIZE = 10000
DEFAULT_DATABASE_URL = 'sqlite://'
DEFAULT_IS_GEOSPATIAL = False
DEFAULT_SCHEMA = None


""" data source constants """
DATASOURCE_GTFS = 1
DATASOURCE_LOOKUP = 2
DATASOURCE_DERIVED = 3


""" geometry constants """
SRID = 4326
