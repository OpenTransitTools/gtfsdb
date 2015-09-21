__author__ = 'rhunter'

from sqlalchemy import Column, Integer, Boolean, String, Sequence, DateTime
from gtfsdb.model.base import Base


class Meta(Base):
    __tablename__ = 'feed_meta_data'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    file_name = Column(String(255))
    completed = Column(Boolean, default=False)
    upload_date = Column(DateTime)

