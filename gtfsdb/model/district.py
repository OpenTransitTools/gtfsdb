import datetime

from sqlalchemy import Column, Sequence
from sqlalchemy.types import Date, Integer, String
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql.functions import func

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.route import Route

import logging
log = logging.getLogger(__file__)


class District(Base):
    """
    Service District bounding geometry
    can be configured to load a service district shape
    or will calculate a boundary based on the extents of the route geometries

    NOTE: to load this table, you need both a geospaitial db (postgis) and the --create_boundaries cmd-line parameter
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

    def intersect(self, point):
        from gtfsdb.util_geo import does_point_intersect_geom
        return does_point_intersect_geom(point, self.geom)

    def distance(self, point):
        from gtfsdb.util_geo import point_to_geom_distance
        return point_to_geom_distance(point, self.geom)

    @classmethod
    def load(cls, db, **kwargs):
        if hasattr(cls, 'geom'):
            log.debug('{0}.load (loaded later in post_process)'.format(cls.__name__))

    @classmethod
    def calculated_boundary(cls, db):
        """
        # Fill holes in buffered district map
        # https://geospatial.commons.gc.cuny.edu/2013/11/04/filling-in-holes-with-postgis/
        # https://postgis.net/docs/ST_ExteriorRing.html
        # NOTE ST_ExteriorRing won't work with MULTIPOLYGONS
        # https://postgis.net/docs/ST_Buffer.html
        """
        from gtfsdb import util_geo

        log.info('calculating the service district boundary from an abitrary buffer / extent on routes')
        geom = db.session.query(
            func.ST_ExteriorRing(
                func.ST_Union(
                    Route.geom.ST_Buffer(0.0085, 'quad_segs=4 endcap=square join=mitre mitre_limit=1.0'))))
        ret_val = func.ST_MakePolygon(geom)
        return ret_val

    @classmethod
    def shp_file_boundary(cls):
        """
        load the boundary geometry from a .shp file
        """
        ret_val = None
        if ret_val is None:
            log.warn('was not able to grab a district boundary from a .shp file')
        return ret_val

    @classmethod
    def post_process(cls, db, **kwargs):
        if hasattr(cls, 'geom') and kwargs.get('create_boundaries'):
            log.debug('{0}.post_process'.format(cls.__name__))
            district = cls(name='District Boundary')

            # make / grab the geometry
            geom = None
            if True: # config.district_boundary_shp_file:
                geom = cls.shp_file_boundary()
            if geom is None:
                geom = cls.calculated_boundary(db)
            district.geom = geom

            db.session.add(district)
            db.session.commit()
            db.session.close()

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            log.debug('{0}.add geom column'.format(cls.__name__))
            cls.geom = deferred(Column(Geometry('POLYGON')))
