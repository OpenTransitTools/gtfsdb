from sqlalchemy import Column
from sqlalchemy.types import Date, String

from gtfsdb import config
from gtfsdb.model.base import Base


class FeedInfo(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'feed_info.txt'

    __tablename__ = 'feed_info'

    feed_publisher_name = Column(String(512), primary_key=True)
    feed_publisher_url = Column(String(1024), nullable=False)
    feed_lang = Column(String(256), nullable=False)
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String(1024))
    feed_license = Column(String(1024))
