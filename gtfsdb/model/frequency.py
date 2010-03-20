from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, Integer, String


class Frequency(DeclarativeBase):
    __tablename__ = 'frequencies'

    required_fields = ['trip_id', 'start_time', 'end_time', 'headway_secs']

    trip_id = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    headway_secs = Column(Integer)

