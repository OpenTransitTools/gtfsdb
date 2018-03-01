import datetime

from sqlalchemy import Column, Sequence
from sqlalchemy.types import Date, Integer, String
from sqlalchemy.orm import deferred, relationship

from gtfsdb import config
from gtfsdb.model.base import Base

import logging
log = logging.getLogger(__file__)


class Ada(Base):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'ada'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, index=True, nullable=False)
    end_date = Column(Date, index=True, nullable=False)

    def __init__(self, name):
        self.name = name
        self.start_date = self.end_date = datetime.datetime.now()

    def geom_from_shape(self, coords):
        #self.geom = 'SRID={0};POLYGON({1})'.format(config.SRID, ','.join(coords))
        self.geom = 'POLYGON(({1}))'.format(config.SRID, coords)

    @classmethod
    def load(cls, db, **kwargs):
        if hasattr(cls, 'geom'):
            log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))

    @classmethod
    def post_process(cls, db, **kwargs):
        if hasattr(cls, 'geom'):
            log.debug('{0}.post_process'.format(cls.__name__))
            ada = cls(name='Garde')
            ada.geom_from_shape("37.9615819622 23.7216281890869,37.9617173039801 23.7193965911865,37.9633413851658 23.717679977417,37.964559422483 23.7147617340087,37.9644240860015 23.7116718292236, 37.9615819622 23.72162818, 37.9615819622 23.7216281890869")
            db.session.add(ada)
            db.session.commit()
            db.session.close()


    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            log.debug('{0}.add geom column'.format(cls.__name__))
            cls.geom = deferred(Column(Geometry('POLYGON')))
