from gtfsdb.model import DeclarativeBase
from sqlalchemy import Boolean, Column, Date, Integer, String


__all__ = ['Calendar', 'CalendarDate']


class Calendar(DeclarativeBase):
    __tablename__ = 'calendar'

    required_fields = ['service_id', 'monday', 'tuesday', 'wednesday',
                       'thursday', 'friday', 'saturday', 'sunday',
                       'start_date', 'end_date']

    service_id = Column(String)
    monday = Column(Boolean)
    tuesday = Column(Boolean)
    wednesday = Column(Boolean)
    thursday = Column(Boolean)
    friday = Column(Boolean)
    saturday = Column(Boolean)
    sunday = Column(Boolean)
    start_date = Column(Date)
    end_date = Column(Date)


class CalendarDate(DeclarativeBase):
    __tablename__ = 'calendar_dates'

    required_fields = ['service_id', 'date', 'exception_type']

    service_id = Column(String)
    date = Column(Date)
    exception_type = Column(Integer)
