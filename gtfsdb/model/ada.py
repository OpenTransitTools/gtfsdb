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


class Ada(Base):
    """
    The Americans with Disabilities Act (https://www.ada.gov) requires transit agencies to provide
    complementary paratransit service to destinations within 3/4 mile of all fixed routes.
    :see: https://en.wikipedia.org/wiki/Paratransit#Americans_with_Disabilities_Act_of_1990

    This class will calculate and represent a Paratransit (or ADA) boundary against all active routes.

    NOTE: to load this table, you need both a geospaitial db (postgis) and the --create_boundaries cmd-line parameter
    """
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'ada'

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
    def post_process(cls, db, **kwargs):
        if hasattr(cls, 'geom') and kwargs.get('create_boundaries'):
            log.debug('{0}.post_process'.format(cls.__name__))
            ada = cls(name='ADA Boundary')

            # 3960 is the number of feet in 3/4 of a mile this is the size of the buffer around routes that
            # is be generated for the ada boundary
            # todo: make this value configurable ... and maybe metric ...
            # todo: the following doesn't work ... too big of a buffer ... so
            # geom = db.session.query(func.ST_Union(Route.geom.ST_Buffer(3960, 'quad_segs=50')))

            # the buffer values here are just guesses at this point ...
            geom = db.session.query(func.ST_Union(Route.geom.ST_Buffer(0.0035)))
            # TODO: clip the ADA geom against the District geom ... no ADA outside legal transit district
            ada.geom = geom

            db.session.add(ada)
            db.session.commit()
            db.session.close()

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            log.debug('{0}.add geom column'.format(cls.__name__))
            cls.geom = deferred(Column(Geometry('POLYGON')))
