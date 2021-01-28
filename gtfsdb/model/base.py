from pkg_resources import resource_filename  # @UnresolvedImport

from gtfsdb import config, util
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import object_session

import csv
import datetime
import os
import sys
import time

import logging
log = logging.getLogger(__name__)


try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


class _Base(object):

    filename = None

    @property
    def session(self):
        #import pdb; pdb.set_trace()
        ret_val = None
        try:
            ret_val = object_session(self)
        except:
            log.warning("can't get a session from object")
        return ret_val

    @classmethod
    def set_schema(cls, schema):
        cls.__table__.schema = schema

    @classmethod
    def get_schema(cls, def_val=None):
        ret_val = def_val
        if hasattr(cls, '__table__') and cls.__table__.schema:
            ret_val = cls.__table__.schema
        return ret_val

    @classmethod
    def make_geom_lazy(cls):
        from sqlalchemy.orm import deferred
        try:
            cls.__mapper__.add_property('geom', deferred(cls.__table__.c.geom))
        except Exception as e:
            log.warning(e)

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.make_record(attrs)
        return cls(**clean_dict)

    @property
    def to_dict(self):
        """
        convert a SQLAlchemy object into a dict that is serializable to JSON
        """
        ret_val = self.__dict__.copy()

        """ not crazy about this hack, but ... the __dict__ on a SQLAlchemy
        object contains hidden crap that we delete from the class dict
        """
        if set(['_sa_instance_state']).issubset(ret_val):
            del ret_val['_sa_instance_state']

        """ we're using 'created' as the date parameter, so convert values
        to strings <TODO>: better would be to detect date & datetime objects,
        and convert those...
        """
        if set(['created']).issubset(ret_val):
            ret_val['created'] = ret_val['created'].__str__()

        return ret_val

    def get_up_date_name(self, attribute_name):
        """
        return attribute name of where we'll store an update variable
        """
        return "{0}_update_utc".format(attribute_name)

    def is_cached_data_valid(self, attribute_name, max_age=2):
        """
        we have to see both the attribute name exist in our object, as well as
        that object having a last update date (@see update_cached_data below)
        and that update date being less than 2 days ago...
        """
        ret_val = False
        try:
            # import pdb; pdb.set_trace()
            if hasattr(self, attribute_name):
                attribute_update = self.get_up_date_name(attribute_name)
                if hasattr(self, attribute_update):
                    epoch = datetime.datetime.utcfromtimestamp(0)
                    delta = getattr(self, attribute_update) - epoch
                    if delta.days <= max_age:
                        ret_val = True
        except:
            log.warning("is_cached_data_valid(): saw a cache exception with attribute {0}".format(attribute_name))
            ret_val = False

        return ret_val

    def update_cached_data(self, attribute_name):
        """
        """
        try:
            # import pdb; pdb.set_trace()
            attribute_update = self.get_up_date_name(attribute_name)
            setattr(self, attribute_update, datetime.datetime.now())
        except:
            log.warning("update_cached_data(): threw an exception with attribute {0}".format(attribute_name))

    @classmethod
    def load(cls, db, **kwargs):
        """
        Load method for ORM

        arguments:
            db: instance of gtfsdb.Database

        keyword arguments:
            gtfs_directory: path to unzipped GTFS files
            batch_size: batch size for memory management
        """

        # step 0: set up some vars, including setting the log output to show the child of base that we're processing
        start_time = time.time()
        batch_size = kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE)
        log = logging.getLogger(cls.__module__)

        # step 1: check that we have elements of a file path (a file name and a directory) for the data we'll load
        if cls.filename is None:
            if cls.datasource is not config.DATASOURCE_DERIVED:
                log.info("{0} didn't specify a 'filename', so won't bohter trying to load() a null file (early exit from load()).".format(cls.__name__))
            return  # note early exit
        if cls.datasource is not config.DATASOURCE_GTFS and cls.datasource is not config.DATASOURCE_LOOKUP:
            log.info("{0}.datasource != DATASOURCE_GTFS or DATASOURCE_LOOKUP (exit load).".format(cls.__name__))
            return  # note early exit

        # step 2: load either a GTFS file from the unzipped file or a resource file (from a dir specified in config)
        directory = None
        if cls.datasource == config.DATASOURCE_GTFS:
            directory = kwargs.get('gtfs_directory')
        elif cls.datasource == config.DATASOURCE_LOOKUP:
            directory = resource_filename('gtfsdb', 'data')

        # step 3: load the file
        log.info("load {0}".format(cls.__name__))
        records = []
        file_path = os.path.join(directory, cls.filename)
        if os.path.exists(file_path):
            if sys.version_info >= (3, 0):
                f = open(file_path, 'rb')
            else:
                f = open(file_path, 'r')
            utf8_file = util.UTF8Recoder(f, 'utf-8-sig')
            reader = csv.DictReader(utf8_file)
            reader.fieldnames = [field.strip().lower() for field in reader.fieldnames]
            table = cls.__table__
            try:
                db.engine.execute(table.delete())
            except:
                log.debug("NOTE: couldn't delete this table")

            i = 0
            for row in reader:
                records.append(cls.make_record(row))
                i += 1
                if i >= batch_size:
                    db.engine.execute(table.insert(), records)
                    sys.stdout.write('*')
                    records = []
                    i = 0
            if len(records) > 0:
                db.engine.execute(table.insert(), records)
            f.close()

        # step 4: done...
        process_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(cls.__name__, process_time))

    @classmethod
    def post_process(cls, db, **kwargs):
        """
        Post-process processing method.  This method is a placeholder
        that may be overridden in children...
        @see: stop_time.py or route.py
        """
        pass

    @classmethod
    def make_record(cls, row):
        for k, v in row.copy().items():
            if isinstance(v, basestring):
                row[k] = v.strip()

            try:
                if k:
                    if (k not in cls.__table__.c):
                        del row[k]
                    elif not v:
                        row[k] = None
                    elif k.endswith('date'):
                        row[k] = datetime.datetime.strptime(v, '%Y%m%d').date()
                else:
                    log.info("I've got issues with your GTFS {0} data.  I'll continue, but expect more errors...".format(cls.__name__))
            except Exception as e:
                log.warning(e)

        """ if this is a geospatially enabled database, add a geom """
        if hasattr(cls, 'geom') and hasattr(cls, 'add_geom_to_dict'):
            cls.add_geom_to_dict(row)

        """ post make_record gives the calling class a chance to fix things up prior to being sent down to database """
        row = cls.post_make_record(row)
        return row

    @classmethod
    def post_make_record(cls, row):
        """ Base does nothing, but a derived class now has a chance to clean up the record prior to db commit """
        return row


Base = declarative_base(cls=_Base)
