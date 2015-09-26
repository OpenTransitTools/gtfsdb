from sqlalchemy import Column, Index
from sqlalchemy.types import String
from sqlalchemy.orm import relationship

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.feed_info import FeedInfo
from gtfsdb.model.guuid import GUID


class Agency(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'agency.txt'

    __tablename__ = 'gtfs_agency'

    agency_id = Column(GUID(), primary_key=True)
    feed_id = Column(GUID())
    file_id = Column(String(32), nullable=False)
    agency_name = Column(String(255), nullable=False)
    agency_url = Column(String(255), nullable=False)
    agency_timezone = Column(String(50), nullable=False)
    agency_lang = Column(String(10))
    agency_phone = Column(String(50))
    agency_fare_url = Column(String(255))

    routes = relationship('Route', backref='agency', primaryjoin='Route.agency_id==Agency.agency_id',
                          foreign_keys='(Route.agency_id)', cascade='delete')

    @classmethod
    def make_record(cls, row, key_lookup, **kwargs):
        if 'agency_id' not in row.keys() or not row['agency_id']:
            row['agency_id']='1'
        if ('feed_id' not in row.keys() or not row['feed_id']) and 'feed_id' in key_lookup.keys():
            if len(key_lookup['feed_id'].keys()) > 1:
                raise Exception("More than one feed Id key and no feed ids labled in agency")
            row['feed_id'] = key_lookup['feed_id'].keys()[0]
        row = super(Agency, cls).make_record(row, key_lookup)
        row['file_id'] = kwargs.get('file_id')
        return row

Index('ix_gtfs_agency_agency_id', Agency.agency_id, postgresql_using='hash')
Index('ix_gtfs_agency_feed_id', Agency.feed_id, postgresql_using='hash')
