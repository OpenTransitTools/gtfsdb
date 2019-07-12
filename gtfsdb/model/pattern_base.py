from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import deferred, relationship

from gtfsdb import config

import logging
log = logging.getLogger(__name__)


class PatternBase(object):
    """
    provides a generic set of pattern query routines, etc...
    """

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = deferred(Column(Geometry(geometry_type='LINESTRING', srid=config.SRID)))

    def geom_from_shape(self, points):
        coords = ['{0} {1}'.format(r.shape_pt_lon, r.shape_pt_lat) for r in points]
        self.geom = 'SRID={0};LINESTRING({1})'.format(config.SRID, ','.join(coords))

    @classmethod
    def get_geometry(cls, session, pattern_id, agency=None):
        """
        simple utility for querying a stop from gtfsdb
        """
        ret_val = None
        try:
            log.info("query Pattern for {}".format(pattern_id_id))
            q = session.query(cls)
            q = q.filter(cls.shape_id == pattern_id)
            # TODO q.filter(cls.agency_id == agency_id)
            ret_val = q.one()
        except Exception as e:
            log.info(e)
        return ret_val

    @classmethod
    def get_geometry_encoded(cls, session, pattern_id, agency=None):
        ret_val = cls.query_orm_for_pattern(session, pattern_id, agency)
        # TODO encode using mapbox or something...
        return ret_val
