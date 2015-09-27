__author__ = 'rhunter'
import uuid

from sqlalchemy import Column, Integer, Boolean, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship

from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID
import datetime

feed_agency_table = Table('feed_agency', Base.metadata,
    Column('file_id', String(32), ForeignKey('gtfs_ex_files.md5sum')),
    Column('ex_agency_id', String(255), ForeignKey('gtfs_exchange_agencies.dataexchange_id'))
)

class FeedFile(Base):
    __tablename__ = 'gtfs_ex_files'

    md5sum = Column(String(32), primary_key=True)
    date_added = Column(DateTime)
    description = Column(String(255))
    file_url = Column(String(255))
    filename = Column(String(255))
    size = Column(Integer)
    uploaded_by_user = Column(String(255))

    completed = Column(Boolean, default=False)
    censio_upload_date = Column(DateTime)

    ex_agencies = relationship('GTFSExAgency',
                            secondary=feed_agency_table,
                            backref='feeds')
    agencies = relationship('Agency', backref="feed_file", primaryjoin='Agency.file_id==FeedFile.md5sum',
                            foreign_keys='(Agency.file_id)', cascade='delete')

    def __init__(self, **kwargs):
        if 'agencies' in kwargs.keys():
            self.ex_agencies = [GTFSExAgency(dataexchange_id=agency) for agency in kwargs.get('agencies')]
        if 'date_added' in kwargs.keys():
            kwargs['date_added'] = datetime.datetime.utcfromtimestamp(kwargs.get('date_added'))
        for key, value in kwargs.iteritems():
            if isinstance(value, basestring):
                kwargs[key]=value[:255]
        super(FeedFile, self).__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, FeedFile) and self.md5sum == other.md5sum:
            return True
        return False

    def __hash__(self):
        return hash(self.md5sum)


class GTFSExAgency(Base):
    __tablename__ = 'gtfs_exchange_agencies'

    dataexchange_id = Column(String(255), primary_key=True, nullable=False)
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
            if 'date_' in key:
                kwargs[key]=datetime.datetime.utcfromtimestamp(value)
            if isinstance(value, basestring):
                kwargs[key]=value[:255]
        super(GTFSExAgency, self).__init__(**kwargs)


