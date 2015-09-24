__author__ = 'rhunter'
import uuid

from sqlalchemy import Column, Integer, Boolean, String, Sequence, DateTime

from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID


class FeedFile(Base):
    __tablename__ = 'gtfs_ex_files'

    dataexchange_id = Column(String(255))
    date_added=Column(DateTime)
    description = Column(String(255))
    file_url = Column(String(255))
    filename = Column(String(255))
    md5sum = Column(String(32), primary_key=True)
    size = Column(Integer)
    uploaded_by_user = Column(String(255))

    completed = Column(Boolean, default=False)
    censio_upload_date = Column(DateTime)

    def __init__(self, agencies, **kwargs):
        self.agencies = agencies
        for key, value in kwargs.iteritems():
            if isinstance(value, basestring):
                kwargs[key]=value[:255]
        super(FeedFile, self).__init__(**kwargs)


class GTFSExFeed(Base):
    __tablename__ = 'gtfs_exchange_feeds'

    dataexchange_id = Column(String(255), primary_key=True)
    area = Column(String(255))
    country = Column(String(255))
    dataexchange_url = Column(String(255))
    date_added = Column(DateTime())
    date_last_updated = Column(DateTime())
    feed_baseurl = Column(String(255))
    is_official = Column(Boolean)
    license_url = Column(String(255))
    name = Column(String(255))
    state = Column(String(255))
    url = Column(String(255))

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if isinstance(value, basestring):
                kwargs[key]=value[:255]
        super(GTFSExFeed, self).__init__(**kwargs)


