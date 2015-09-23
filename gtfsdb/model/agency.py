from sqlalchemy import Column
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
    agency_name = Column(String(255), nullable=False)
    agency_url = Column(String(255), nullable=False)
    agency_timezone = Column(String(50), nullable=False)
    agency_lang = Column(String(10))
    agency_phone = Column(String(50))
    agency_fare_url = Column(String(255))

    routes = relationship('Route', backref='agency', primaryjoin='Route.agency_id==Agency.agency_id',
                          foreign_keys='(Route.agency_id)')

    @classmethod
    def make_record(cls, row, key_lookup):
        if 'agency_id' not in row.keys():
            row['agency_id']='1'
        return super(Agency, cls).make_record(row, key_lookup)

