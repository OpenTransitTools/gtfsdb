import time

from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql import func

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.shape import Shape
from gtfsdb.model.pattern_base import PatternBase

import logging
log = logging.getLogger(__name__)


__all__ = ['Pattern']


class Pattern(Base, PatternBase):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'patterns'

    shape_id = Column(String(255), primary_key=True, index=True)
    pattern_dist = Column(Numeric(20, 10))

    trips = relationship(
        'Trip',
        primaryjoin='Pattern.shape_id==Trip.shape_id',
        foreign_keys='(Pattern.shape_id)',
        uselist=True, viewonly=True)

    shapes = relationship(
        'Shape',
        primaryjoin='Pattern.shape_id==Shape.shape_id',
        foreign_keys='(Shape.shape_id)',
        uselist=True, viewonly=True)

    @classmethod
    def load(cls, db, **kwargs):
        start_time = time.time()
        session = db.session
        q = session.query(
            Shape.shape_id,
            func.max(Shape.shape_dist_traveled).label('dist')
        )
        shapes = q.group_by(Shape.shape_id)
        for shape in shapes:
            pattern = cls()
            pattern.shape_id = shape.shape_id
            pattern.pattern_dist = shape.dist
            if hasattr(cls, 'geom'):
                q = session.query(Shape)
                q = q.filter(Shape.shape_id == shape.shape_id)
                q = q.order_by(Shape.shape_pt_sequence)
                pattern.geom_from_shape(q)
            session.add(pattern)
        session.commit()
        session.close()
        processing_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(cls.__name__, processing_time))
