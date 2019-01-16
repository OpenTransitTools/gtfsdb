import datetime
import logging
import time

from sqlalchemy import Column, Index
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.types import Date, SmallInteger, Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


__all__ = ['Calendar', 'CalendarDate', 'UniversalCalendar']


log = logging.getLogger(__name__)


class Calendar(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'calendar.txt'

    __tablename__ = 'calendar'
    __table_args__ = (Index('calendar_ix1', 'start_date', 'end_date'),)

    service_id = Column(String(255), primary_key=True, index=True, nullable=False)
    monday = Column(SmallInteger, nullable=False)
    tuesday = Column(SmallInteger, nullable=False)
    wednesday = Column(SmallInteger, nullable=False)
    thursday = Column(SmallInteger, nullable=False)
    friday = Column(SmallInteger, nullable=False)
    saturday = Column(SmallInteger, nullable=False)
    sunday = Column(SmallInteger, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    service_name = Column(String(255))  # Trillium extension, a human-readable name for the calendar.

    def weekday_list(self):
        weekday_dict = dict(monday=0, tuesday=1, wednesday=2, thursday=3, friday=4, saturday=5, sunday=6)
        item_func = weekday_dict.iteritems if hasattr(weekday_dict, 'iteritems') else weekday_dict.items
        return [v for k, v in item_func() if getattr(self, k)]

    def to_date_list(self):
        """
        TODO: we need better date limiting management here ... this routine could spin a long time w/forever dates
        TODO: for example, if the begin date is 1900 or end date is 9999, then that'll cause a major slowdown
        """
        date_list = []
        weekdays = self.weekday_list()
        diff = self.end_date - self.start_date
        for i in range(diff.days + 1):
            d = self.start_date + datetime.timedelta(days=i)
            if d.weekday() in weekdays:
                date_list.append(dict(service_id=self.service_id, date=d))
        return date_list


class CalendarDate(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'calendar_dates.txt'

    __tablename__ = 'calendar_dates'

    service_id = Column(String(255), primary_key=True, index=True, nullable=False)
    date = Column(Date, primary_key=True, index=True, nullable=False)
    exception_type = Column(Integer, nullable=False)

    @hybrid_property
    def is_addition(self):
        return self.exception_type == 1

    @hybrid_property
    def is_removal(self):
        return self.exception_type == 2


class UniversalCalendar(Base):
    datasource = config.DATASOURCE_DERIVED
    __tablename__ = 'universal_calendar'

    service_id = Column(String(255), primary_key=True, index=True, nullable=False)
    date = Column(Date, primary_key=True, index=True, nullable=False)

    trips = relationship(
        'Trip',
        primaryjoin='UniversalCalendar.service_id==Trip.service_id',
        foreign_keys='(UniversalCalendar.service_id)',
        uselist=True, viewonly=True)

    @classmethod
    def load(cls, db, **kwargs):
        start_time = time.time()
        session = db.session
        for c in session.query(Calendar):
            session.add_all([cls(**r) for r in c.to_date_list()])
        session.commit()
        q = session.query(CalendarDate)
        for calendar_date in q:
            cd_kwargs = dict(date=calendar_date.date,
                             service_id=calendar_date.service_id)
            if calendar_date.is_addition:
                session.merge(cls(**cd_kwargs))
            if calendar_date.is_removal:
                session.query(cls).filter_by(**cd_kwargs).delete()
        session.commit()
        process_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(cls.__name__, process_time))
