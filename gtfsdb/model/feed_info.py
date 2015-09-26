from sqlalchemy import Column, Sequence, Index
from sqlalchemy.types import Date, DateTime, String, Integer, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import relationship

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID
import logging

log = logging.getLogger(__name__)




class FeedInfo(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'feed_info.txt'

    __tablename__ = 'gtfs_feed_info'

    feed_id = Column(GUID(), primary_key=True)
    feed_publisher_name = Column(String(255))
    feed_publisher_url = Column(String(255), nullable=False)
    feed_lang = Column(String(255), nullable=False)
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String(255))
    feed_license = Column(String(255))

    agencies = relationship('Agency', backref="feed", primaryjoin='Agency.feed_id==FeedInfo.feed_id',
                            foreign_keys='(Agency.feed_id)', cascade='delete')

    @classmethod
    def make_record(cls, row, key_lookup, **kwargs):
        if 'feed_id' not in row.keys() or not row['feed_id']:
            row['feed_id'] = '1'
        return super(FeedInfo, cls).make_record(row, key_lookup, **kwargs)

Index('ix_gtfs_feed_info_feed_id', FeedInfo.feed_id, postgresql_using='hash')

