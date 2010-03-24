from gtfsdb.model import DeclarativeBase
from sqlalchemy import Boolean, Column, Date, Integer, String


__all__ = ['Calendar', 'CalendarDate']


class Calendar(DeclarativeBase):
    __tablename__ = 'calendar'

    required_fields = ['service_id', 'monday', 'tuesday', 'wednesday',
                       'thursday', 'friday', 'saturday', 'sunday',
                       'start_date', 'end_date']

    service_id = Column(String, primary_key=True)
    monday = Column(Boolean, nullable=False)
    tuesday = Column(Boolean, nullable=False)
    wednesday = Column(Boolean, nullable=False)
    thursday = Column(Boolean, nullable=False)
    friday = Column(Boolean, nullable=False)
    saturday = Column(Boolean, nullable=False)
    sunday = Column(Boolean, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)


class CalendarDate(DeclarativeBase):
    __tablename__ = 'calendar_dates'

    required_fields = ['service_id', 'date', 'exception_type']

    service_id = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    exception_type = Column(Integer, nullable=False)
