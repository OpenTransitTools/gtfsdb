from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Agency(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'agency.txt'

    __tablename__ = 'agency'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    agency_id = Column(String(512), index=True, unique=True)
    agency_name = Column(String(512), nullable=False)
    agency_url = Column(String(1024), nullable=False)
    agency_timezone = Column(String(50), nullable=False)
    agency_lang = Column(String(10))
    agency_phone = Column(String(50))
    agency_fare_url = Column(String(1024))
    agency_email = Column(String(1024))
    feed_id = Column(String(512))  # optional field that's used in multiple apps, ala OTP

    def feed_agency_id(self):
        """
        return an feed_id:agency_id pair
        """
        return "{}:{}".format(self.feed_id, self.agency_id)

    @classmethod
    def post_make_record(cls, row, **kwargs):
        try:
            #import pdb; pdb.set_trace()
            row['feed_id'] = kwargs['feed_id']
        except:
            pass
        return row
        