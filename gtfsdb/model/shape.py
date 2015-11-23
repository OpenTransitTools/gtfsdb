import logging
import time

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String, Sequence, Index
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql import func

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID

from sqlalchemy import distinct



__all__ = ['ShapeGeom', 'Shape']


log = logging.getLogger(__name__)


class ShapeGeom(Base):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'gtfs_shape_geoms'

    shape_id = Column(GUID(), primary_key=True, nullable=False)
    the_geom = Column(Geometry(geometry_type='LINESTRING', srid=config.SRID))

    trips = relationship(
        'Trip',
        primaryjoin='ShapeGeom.shape_id==Trip.shape_id',
        foreign_keys='(ShapeGeom.shape_id)',
        uselist=True, viewonly=True)

    @classmethod
    def add_geometry_column(cls):
        #TODO Get rid of this
        pass

    def geom_from_shape(self, points):
        coords = ['{0} {1}'.format(r.shape_pt_lon, r.shape_pt_lat) for r in points]
        self.the_geom = 'SRID={0};LINESTRING({1})'.format(config.SRID, ','.join(coords))

    @classmethod
    def get_shape_list(cls, session):
        shape_geoms = session.query(ShapeGeom.shape_id).subquery()
        return session.query(distinct(Shape.shape_id))\
            .filter(Shape.shape_id.notin_(shape_geoms)).all()

    @classmethod
    def create_shape_geom(cls, shape_id, session):
        shape_geom = cls()
        shape_geom.shape_id = shape_id
        q = session.query(Shape)\
            .filter(Shape.shape_id == shape_id)\
            .order_by(Shape.shape_pt_sequence)
        shape_geom.geom_from_shape(q)
        return shape_geom

    @classmethod
    def load(cls, db, **kwargs):
        start_time = time.time()
        session = db.get_session()
        shapes = cls.get_shape_list(session)
        for shape in shapes:
            shape_geom = cls.create_shape_geom(shape.shape_id, session)
            session.merge(shape_geom)
        session.commit()
        session.close()
        processing_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(
            cls.__name__, processing_time))

Index('ix_gtfs_shape_geom_shape_id', ShapeGeom.shape_id, postgresql_using='hash')

class Shape(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'shapes.txt'

    __tablename__ = 'gtfs_shapes'

    id = Column(GUID(), primary_key=True, nullable=True)
    shape_id = Column(GUID(), nullable=False)
    shape_pt_lat = Column(Numeric(12, 9), nullable=False)
    shape_pt_lon = Column(Numeric(12, 9), nullable=False)
    shape_pt_sequence = Column(Integer, primary_key=True)
    shape_dist_traveled = Column(Numeric(20, 10))
    the_geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def add_geometry_column(cls):
        #TODO: Get Rid of this
        pass

    @classmethod
    def add_geom_to_dict(cls, row):
        args = (config.SRID, row['shape_pt_lon'], row['shape_pt_lat'])
        row['the_geom'] = 'SRID={0};POINT({1} {2})'.format(*args)

Index('ix_gtfs_shape_shape_id', Shape.shape_id, postgresql_using='hash')
Index('ix_gtfs_shape_shape_dist_traveled', Shape.shape_dist_traveled)
