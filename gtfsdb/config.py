from ConfigParser import ConfigParser
import logging.config
import os
from pkg_resources import resource_filename


config = ConfigParser()
config.read(os.path.join(resource_filename('gtfsdb', 'configs'), 'app.ini'))
if config.has_section('loggers'):
    logging.config.fileConfig(ini_file, disable_existing_loggers=False)
