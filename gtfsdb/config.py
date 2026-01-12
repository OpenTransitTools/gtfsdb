try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import os
import logging.config


# import pdb; pdb.set_trace()
""" parse configuration file and setup logging """
config = ConfigParser()
ini_file = os.path.join(os.path.dirname(__file__), 'configs', 'app.ini')
config.read(ini_file)
if config.has_section('loggers'):
    logging.config.fileConfig(ini_file, disable_existing_loggers=False)


def get_value(key, section="general", def_val=None):
    try:
        ret_val =config.get(section, key)
    except:
        ret_val = def_val
    return ret_val


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


""" misc defaults """
default_route_color = get_value("default_route_color", def_val="#7B97B2")
default_frequent_color = get_value("default_frequent_color", def_val="#306095")
default_text_color = get_value("default_text_color", def_val="#FFFFFF")
