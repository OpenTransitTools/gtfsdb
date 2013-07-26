import datetime
import logging
import time

from sqlalchemy import Column, Index
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.types import Boolean, Date, Integer, String

from gtfsdb.model.base import Base


__all__ = ['Calendar', 'CalendarDate', 'UniversalCalendar']


log = logging.getLogger(__name__)


class Calendar(Base):
    __tablename__ = 'calendar'
    __table_args__ = (Index('calendar_ix1', 'start_date', 'end_date'),)

    service_id = Column(String(255), primary_key=True, nullable=False)
    monday = Column(Boolean, nullable=False)
    tuesday = Column(Boolean, nullable=False)
    wednesday = Column(Boolean, nullable=False)
    thursday = Column(Boolean, nullable=False)
    friday = Column(Boolean, nullable=False)
    saturday = Column(Boolean, nullable=False)
    sunday = Column(Boolean, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    def weekday_list(self):
        day_list = []
        if self.monday:
            day_list.append(0)
        if self.tuesday:
            day_list.append(1)
        if self.wednesday:
            day_list.append(2)
        if self.thursday:
            day_list.append(3)
        if self.friday:
            day_list.append(4)
        if self.saturday:
            day_list.append(5)
        if self.sunday:
            day_list.append(6)
        return day_list

    def to_date_list(self):
        date_list = []
        d = self.start_date
        delta = datetime.timedelta(days=1)
        weekdays = self.weekday_list()
        while d <= self.end_date:
            if d.weekday() in weekdays:
                kwargs = dict(
                    service_id=self.service_id,
                    date=d)
                date_list.append(kwargs)
            d += delta
        return date_list


class CalendarDate(Base):
    __tablename__ = 'calendar_dates'

    service_id = Column(String(255), primary_key=True, nullable=False)
    date = Column(Date, primary_key=True, index=True, nullable=False)
    exception_type = Column(Integer, nullable=False)

    @property
    def is_addition(self):
        return self.exception_type == 1

    @property
    def is_removal(self):
        return self.exception_type == 2


class UniversalCalendar(Base):
    __tablename__ = 'universal_calendar'

    service_id = Column(String(255), primary_key=True, nullable=False)
    date = Column(Date, primary_key=True, index=True, nullable=False)

    trips = relationship('Trip',
        primaryjoin='Trip.service_id==UniversalCalendar.service_id',
        foreign_keys=(service_id),
        viewonly=True)

    @classmethod
    def get_filename(cls):
        return None

    @classmethod
    def from_calendar_date(cls, calendar_date):
        kwargs = dict(
            date=calendar_date.date,
            service_id=calendar_date.service_id,
        )
        return cls(**kwargs)

    @classmethod
    def load(cls, engine):
        start_time = time.time()
        Session = sessionmaker(bind=engine)
        session = Session()
        q = session.query(Calendar)
        for calendar in q:
            for row in calendar.to_date_list():
                session.add(cls(**row))
        session.commit()
        q = session.query(CalendarDate)
        for calendar_date in q:
            if calendar_date.is_addition:
                uc = cls.from_calendar_date(calendar_date)
                session.merge(uc)
            if calendar_date.is_removal:
                kwargs = dict(
                    service_id=calendar_date.service_id,
                    date=calendar_date.date)
                session.query(cls).filter_by(**kwargs).delete()
        session.commit()
        session.close()
        process_time = time.time() - start_time
        log.debug('UniversalCalendar ({0:.0f} seconds)'.format(process_time))
