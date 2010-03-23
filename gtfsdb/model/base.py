from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.ext.declarative import DeclarativeMeta


__all__ = ['BaseMeta', 'Base']


class BaseMeta(DeclarativeMeta):

    def __init__(cls, name, bases, attrs):
        if name not in ('RouteType', 'Shape', 'StopTime', 'Trip'):
            attrs['id'] = Column(Integer, Sequence(None, optional=True), primary_key=True)
        DeclarativeMeta.__init__(cls, name, bases, attrs)


class Base(object):

    @classmethod
    def get_filename(cls):
        return '%s.txt' %(cls.__tablename__)

    @classmethod
    def make_record(cls, row):
        row = cls.clean_dict(row)
        return row


    @classmethod
    def clean_dict(cls, attrs):
        for k, v in attrs.items():
            if v is None or v.strip() == '' or (k not in cls.__table__.c):
                del attrs[k]
        return attrs

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.clean_dict(attrs)
        c = cls(**clean_dict)
        return c

    @classmethod
    def set_schema(cls, schema):
        cls.__table__.schema = schema

    @classmethod
    def get_srid(cls):
        return 4326

    @classmethod
    def validate(cls, fieldnames):
        try:
            required_fields = cls.required_fields
        except AttributeError:
            required_fields = []
        try:
            optional_fields = cls.optional_fields
        except AttributeError:
            optional_fields = []
        try:
            proposed_fields = cls.proposed_fields
        except AttributeError:
            proposed_fields = []
        all_fields = required_fields + optional_fields + proposed_fields

        # required fields
        fields = None
        if required_fields and fieldnames:
            fields = set(required_fields) - set(fieldnames)
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
