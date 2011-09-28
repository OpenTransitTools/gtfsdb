from sqlalchemy import Column, Index, Sequence
from sqlalchemy.types import Date, String

from .base import Base


class FeedInfo(Base):
    __tablename__ = 'feed_info'

    required_fields = ['feed_publisher_name', 'feed_publisher_url', 'feed_lang']
    optional_fields = ['feed_start_date', 'feed_end_date', 'feed_version']

    feed_publisher_name = Column(String, primary_key=True)
    feed_publisher_url = Column(String, nullable=False)
    feed_lang = Column(String, nullable=False)
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String)
