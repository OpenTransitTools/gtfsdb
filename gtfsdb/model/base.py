import csv
import os
import sys
import time


class Base(object):

    required_fields = []
    optional_fields = []
    proposed_fields = []

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.make_record(attrs)
        c = cls(**clean_dict)
        return c

    @classmethod
    def get_filename(cls):
        return '%s.txt' %(cls.__tablename__)
    
    @classmethod
    def load(cls, engine, directory=None, validate=True):
        records = []
        file_path = '%s/%s' %(directory, cls.get_filename())
        if os.path.exists(file_path):
            start_time = time.time()
            file = open(file_path)
            reader =  csv.DictReader(file)
            if validate:
                cls.validate(reader.fieldnames)
            s = ' - %s ' %(cls.get_filename())
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

    @classmethod
    def make_record(cls, row):
        # clean dict
        for k, v in row.items():
            if v is None or v.strip() == '' or (k not in cls.__table__.c):
                del row[k]
        # add geometry to dict
        if hasattr(cls, 'add_geom_to_dict'):
            cls.add_geom_to_dict(row)
        return row

    @classmethod
    def set_schema(cls, schema):
        cls.__table__.schema = schema

    @classmethod
    def validate(cls, fieldnames):
        all_fields = cls.required_fields + cls.optional_fields + cls.proposed_fields

        # required fields
        fields = None
        if cls.required_fields and fieldnames:
            fields = set(cls.required_fields) - set(fieldnames)
        if fields:
            missing_required_fields = list(fields)
            if missing_required_fields:
                print ' %s missing fields: %s' %(cls.get_filename(), missing_required_fields)

        # all fields
        fields = None
        if all_fields and fieldnames:
            fields = set(fieldnames) - set(all_fields)
        if fields:
            unknown_fields = list(fields)
            if unknown_fields:
                print ' %s unknown fields: %s' %(cls.get_filename(), unknown_fields)
