from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String

from gtfsdb.model.base import Base


class Agency(Base):
    __tablename__ = 'agency'

    required_fields = ['agency_name', 'agency_url', 'agency_timezone']
    optional_fields = ['agency_id', 'agency_lang', 'agency_phone',
                       'agency_fare_url']

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    agency_id = Column(String, index=True, unique=True)
    agency_name = Column(String, nullable=False)
    agency_url = Column(String, nullable=False)
    agency_timezone = Column(String, nullable=False)
    agency_lang = Column(String)
    agency_phone = Column(String)
    agency_fare_url = Column(String)
