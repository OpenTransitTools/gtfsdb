import csv
import datetime
import logging
import os
import sys
import time

from sqlalchemy.ext.declarative import declarative_base

from gtfsdb import util


log = logging.getLogger(__name__)


class _Base(object):

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.make_record(attrs)
        c = cls(**clean_dict)
        return c

    def to_dict(self):
        ''' convert a SQLAlchemy object into a dict that is serializable to JSON
        '''
        ret_val = self.__dict__.copy()

        ''' not crazy about this hack, but ... 
            the __dict__ on a SQLAlchemy object contains hidden crap that we delete from the class dict
        '''
        if set(['_sa_instance_state']).issubset(ret_val):
            del ret_val['_sa_instance_state']

        ''' we're using 'created' as the date parameter, so convert values to strings
            TODO: better would be to detect date & datetime objects, and convert those...
        '''
        if set(['created']).issubset(ret_val):
            ret_val['created'] = ret_val['created'].__str__();

        return ret_val 

    @classmethod
    def get_filename(cls):
        return '%s.txt' % (cls.__tablename__)

    @classmethod
    def load(cls, engine, directory=None, validate=True):
        records = []
        file_path = '%s/%s' % (directory, cls.get_filename())
        if os.path.exists(file_path):
            start_time = time.time()
            f = open(file_path, 'r')
            utf8_file = util.UTF8Recoder(f, 'utf-8-sig')
            reader = csv.DictReader(utf8_file)
            if validate:
                cls.validate(reader.fieldnames)
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
            f.close()
            processing_time = time.time() - start_time
            log.debug('{0} ({1:.0f} seconds)'.format(
                cls.get_filename(), processing_time))

    @classmethod
    def make_record(cls, row):
        # clean dict
        for k, v in row.items():
            if isinstance(v, basestring):
                v = v.strip()
            if (k not in cls.__table__.c):
                del row[k]
            elif not v:
                row[k] = None
            elif k.endswith('date'):
                row[k] = datetime.datetime.strptime(v, '%Y%m%d').date()
        # add geometry to dict
        if hasattr(cls, 'add_geom_to_dict'):
            cls.add_geom_to_dict(row)
        return row

    @classmethod
    def validate(cls, fieldnames):
        if not fieldnames:
            return
        cols = cls.__table__.columns
        all_fields = [c.name for c in cols]
        required_fields = [c.name for c in cols if c.nullable == False]
        missing_fields = list(set(required_fields) - set(fieldnames))
        unknown_fields = list(set(fieldnames) - set(all_fields))

        if missing_fields:
            log.debug('{0} missing fields: {1}'.format(
                cls.get_filename(), missing_fields))
        if unknown_fields:
            log.debug('{0} unknown fields: {1}'.format(
                cls.get_filename(), unknown_fields))

Base = declarative_base(cls=_Base)
