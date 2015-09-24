import csv
import datetime
import logging
import os
from pkg_resources import resource_filename  # @UnresolvedImport
import sys
import time
import uuid

from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import object_session
from gtfsdb import config, util

from sqlalchemy.types import String
from sqlalchemy import Column


log = logging.getLogger(__name__)

class _Base(object):

    filename = None
    unique_id = None

    @property
    def session(self):
        ret_val = None
        try:
            ret_val = object_session(self)
        except:
            log.warn("can't get a session from object")
        return ret_val

    @classmethod
    def make_geom_lazy(cls):
        from sqlalchemy.orm import deferred 
        try:
            cls.__mapper__.add_property('the_geom', deferred(cls.__table__.c.the_geom))
        except Exception, e:
            log.warn(e)

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.make_record(attrs)
        return cls(**clean_dict)

    @property
    def to_dict(self):
        '''convert a SQLAlchemy object into a dict that is serializable to JSON
        '''
        ret_val = self.__dict__.copy()

        ''' not crazy about this hack, but ... the __dict__ on a SQLAlchemy
        object contains hidden crap that we delete from the class dict
        '''
        if set(['_sa_instance_state']).issubset(ret_val):
            del ret_val['_sa_instance_state']

        ''' we're using 'created' as the date parameter, so convert values
        to strings <TODO>: better would be to detect date & datetime objects,
        and convert those...
        '''
        if set(['created']).issubset(ret_val):
            ret_val['created'] = ret_val['created'].__str__()

        return ret_val

    def get_up_date_name(self, attribute_name):
        ''' return attribute name of where we'll store an update variable
        '''
        return "{0}_update_utc".format(attribute_name)

    def is_cached_data_valid(self, attribute_name, max_age=2):
        ''' we have to see both the attribute name exist in our object, as well as
            that object having a last update date (@see update_cached_data below)
            and that update date being less than 2 days ago...
        '''
        ret_val = False
        try:
            #import pdb; pdb.set_trace()
            if hasattr(self, attribute_name):
                attribute_update = self.get_up_date_name(attribute_name)
                if hasattr(self, attribute_update):
                    epoch = datetime.datetime.utcfromtimestamp(0)
                    delta = getattr(self, attribute_update) - epoch
                    if delta.days <= max_age:
                        ret_val = True
        except:
            log.warn("is_cached_data_valid(): saw a cache exception with attribute {0}".format(attribute_name))
            ret_val = False

        return ret_val

    def update_cached_data(self, attribute_name):
        '''
        '''
        try:
            #import pdb; pdb.set_trace()
            attribute_update = self.get_up_date_name(attribute_name)
            setattr(self, attribute_update, datetime.datetime.now())
        except:
            log.warn("update_cached_data(): threw an exception with attribute {0}".format(attribute_name))

    @classmethod
    def load(cls, db, key_lookup, **kwargs):
        '''Load method for ORM

        arguments:
            db: instance of gtfsdb.Database

        keyword arguments:
            gtfs_directory: path to unzipped GTFS files
            batch_size: batch size for memory management
        '''
        log = logging.getLogger(cls.__module__)
        start_time = time.time()
        batch_size = kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE)
        directory = None
        if cls.datasource == config.DATASOURCE_GTFS:
            directory = kwargs.get('gtfs_directory')
        elif cls.datasource == config.DATASOURCE_LOOKUP:
            directory = resource_filename('gtfsdb', 'data')

        thread_pool = ThreadPoolExecutor(max_workers=1)

        records = []
        futures = []
        file_path = os.path.join(directory, cls.filename)
        if os.path.exists(file_path):
            f = open(file_path, 'r')
            utf8_file = util.UTF8Recoder(f, 'utf-8-sig')
            reader = csv.DictReader(utf8_file)
            reader.fieldnames = [field.strip().lower() for field in reader.fieldnames]
            table = cls.__table__

            i = 0
            for row in reader:
                record = cls.make_record(row, key_lookup)
                records.append(record)
                i += 1
                if i >= batch_size:
                    futures.append(thread_pool.submit(db.execute, table.insert(), records))
                    records = []
                    i = 0
            if len(records) > 0:
                futures.append(thread_pool.submit(db.execute, table.insert(), records))
            f.close()

        for future in futures:
            while future.running():
                time.sleep(1)
            future.result()
        process_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(cls.__name__, process_time))


    @classmethod
    def post_process(cls, db, **kwargs):
        '''Post-process processing method.  This method is a placeholder
           that may be overridden in children...
           @see: stop_time.py
        '''
        pass

    @classmethod
    def make_record(cls, row, key_lookup):
        for k, v in row.items():
            if isinstance(v, basestring):
                v = v.strip()
                row[k] = v[:254]
            try:
                if k:
                    if (k not in cls.__table__.c):
                        del row[k]
                    elif not v or v.strip() == "":
                        row[k] = None
                    elif k.endswith('date'):
                        row[k] = datetime.datetime.strptime(v, '%Y%m%d').date()
                    elif '_id' in k:
                        v_san = str(v)
                        if k not in key_lookup.keys():
                            key_lookup[k] = dict()
                        if v_san not in key_lookup[k].keys():
                            key_lookup[k][str(v_san)] = uuid.uuid4()
                        row[k] = key_lookup[k][str(v_san)]
                else:
                    log.warning("I've got issues with your GTFS {0} data.  I'll continue, but expect more errors...".format(cls.__name__))
            except Exception, e:
                log.error(e)

        '''if this is a geospatially enabled database, add a geom'''
        if hasattr(cls, 'the_geom') and hasattr(cls, 'add_geom_to_dict'):
            cls.add_geom_to_dict(row)
        return row

Base = declarative_base(cls=_Base)
