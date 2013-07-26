from ConfigParser import ConfigParser
import logging.config
import os
from pkg_resources import get_distribution


ini_file = os.path.join(get_distribution('gtfsdb').location, 'app.ini')
config = ConfigParser()
config.read(ini_file)
if config.has_section('loggers'):
    logging.config.fileConfig(ini_file, disable_existing_loggers=False)
