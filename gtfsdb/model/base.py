import csv
import datetime
import logging
import os
from pkg_resources import resource_filename  # @UnresolvedImport
import sys
import time

from sqlalchemy.ext.declarative import declarative_base

from gtfsdb import config, util


log = logging.getLogger(__name__)


class _Base(object):

    filename = None

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.make_record(attrs)
        return cls(**clean_dict)

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

    @classmethod
    def load(cls, db, directory=None, validate=True, batch_size=10000):
        records = []
        file_path = os.path.join(directory, cls.filename)
        if os.path.exists(file_path):
            start_time = time.time()
            f = open(file_path, 'r')
            utf8_file = util.UTF8Recoder(f, 'utf-8-sig')
            reader = csv.DictReader(utf8_file)
            reader.fieldnames = [field.strip().lower()
                                 for field in reader.fieldnames]
            table = cls.__table__
            db.engine.execute(table.delete())
            i = 0
            for row in reader:
                records.append(cls.make_record(row))
                i += 1
                # commit every `batch_size` records to manage memory
                if i >= batch_size:
                    db.engine.execute(table.insert(), records)
                    sys.stdout.write('*')
                    records = []
                    i = 0
            if len(records) > 0:
                db.engine.execute(table.insert(), records)
            f.close()
            processing_time = time.time() - start_time
            log.debug('{0} ({1:.0f} seconds)'.format(
                cls.filename, processing_time))

    @classmethod
    def make_record(cls, row):
        for k, v in row.items():
            if isinstance(v, basestring):
                row[k] = v.strip()
            if (k not in cls.__table__.c):
                del row[k]
            elif not v:
                row[k] = None
            elif k.endswith('date'):
                row[k] = datetime.datetime.strptime(v, '%Y%m%d').date()
        '''if this is a geospatially enabled database, add a geom'''
        if hasattr(cls, 'geom') and hasattr(cls, 'add_geom_to_dict'):
            cls.add_geom_to_dict(row)
        return row


Base = declarative_base(cls=_Base)
