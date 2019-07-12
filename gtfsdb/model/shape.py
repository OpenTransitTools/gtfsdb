from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String

from gtfsdb import config
from gtfsdb.model.base import Base

import logging
log = logging.getLogger(__name__)


__all__ = ['Shape']


class Shape(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'shapes.txt'

    __tablename__ = 'shapes'

    shape_id = Column(String(255), primary_key=True, index=True)
    shape_pt_lat = Column(Numeric(12, 9))
    shape_pt_lon = Column(Numeric(12, 9))
    shape_pt_sequence = Column(Integer, primary_key=True, index=True)
    shape_dist_traveled = Column(Numeric(20, 10))

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = Column(Geometry(geometry_type='POINT', srid=config.SRID))

    @classmethod
    def add_geom_to_dict(cls, row):
        args = (config.SRID, row['shape_pt_lon'], row['shape_pt_lat'])
        row['geom'] = 'SRID={0};POINT({1} {2})'.format(*args)
