import datetime

from sqlalchemy import Column, Sequence
from sqlalchemy.types import Date, Integer, String
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql.functions import func
from geoalchemy2 import Geometry
from geoalchemy2.functions import GenericFunction

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.route import Route

import logging
log = logging.getLogger(__file__)


class ST_ExteriorRing(GenericFunction):
    name = 'ST_ExteriorRing'
    type = Geometry


class ST_MakePolygon(GenericFunction):
    name = 'ST_MakePolygon'
    type = Geometry


class ST_Collect(GenericFunction):
    name = 'ST_Collect'
    type = Geometry


class District(Base):
    """
    Service District bounding geometry
    can be configured to load a service district shape
    or will calculate a boundary based on the extents of the route geometries
    """
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'district'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, index=True, nullable=False)
    end_date = Column(Date, index=True, nullable=False)

    def __init__(self, name):
        self.name = name
        self.start_date = self.end_date = datetime.datetime.now()

    @classmethod
    def load(cls, db, **kwargs):
        if hasattr(cls, 'geom'):
            log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))

    @classmethod
    def post_process(cls, db, **kwargs):
        if hasattr(cls, 'geom'):
            log.debug('{0}.post_process'.format(cls.__name__))
            district = cls(name='District Boundary')

            # Fill Holes in
            # https://geospatial.commons.gc.cuny.edu/2013/11/04/filling-in-holes-with-postgis/
            # https://postgis.net/docs/ST_ExteriorRing.html
            # NOTE ST_ExteriorRing won't work with MULTIPOLYGONS
            # https://postgis.net/docs/ST_Buffer.html
            geom = db.session.query(
                func.ST_ExteriorRing(
                    func.ST_Union(
                        Route.geom.ST_Buffer(0.0085, 'quad_segs=4 endcap=square join=mitre mitre_limit=1.0'))))
            district.geom = func.ST_MakePolygon(geom)

            db.session.add(district)
            db.session.commit()
            db.session.close()

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            log.debug('{0}.add geom column'.format(cls.__name__))
            cls.geom = deferred(Column(Geometry('POLYGON')))
