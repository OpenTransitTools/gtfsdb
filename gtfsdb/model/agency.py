from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, String


class Agency(DeclarativeBase):
    __tablename__ = 'agency'

    required_fields = ['agency_name', 'agency_url', 'agency_timezone']
    optional_fields = ['agency_id', 'agency_lang', 'agency_phone']
    proposed_fields = ['agency_fare_url']

    agency_id = Column(String)
    agency_name = Column(String)
    agency_url = Column(String)
    agency_timezone = Column(String)
    agency_lang = Column(String)
    agency_phone = Column(String)
    agency_fare_url = Column(String)

