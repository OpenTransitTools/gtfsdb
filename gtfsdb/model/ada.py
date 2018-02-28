from sqlalchemy import Column, Sequence
from sqlalchemy.types import Date, Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Ada(Base):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'ada'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    start_date = Column(Date, index=True, nullable=False)
    end_date = Column(Date, index=True, nullable=False)

    @classmethod
    def load(cls, db, **kwargs):
        log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            cls.geom = deferred(Column(Geometry('POLYGON')))

