from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql import func

from gtfsdb import config, util

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
        """
        builds a linestring geometry for the shape from an array of points
        :return: will return True if there are 2+ points, and False when less than 2 points (not a line)
        """
        coords = [util.make_coord_from_point(r.shape_pt_lon, r.shape_pt_lat) for r in points]
        self.geom = util.make_linestring_from_point_array(coords)

        # test and warn if trying to create a pattern (line) of less than 1 coord
        ret_val = True
        if len(coords) < 2:
            log.warning("a 'linestring' needs 2+ points ({0}); expect a postgis error unless fixed".format(coords))
            ret_val = False
        return ret_val

    @classmethod
    def query_pattern(cls, session, pattern_id, agency=None):
        """
        simple utility for querying a stop from gtfsdb
        """
        ret_val = None
        try:
            log.info("query Pattern for {}".format(pattern_id))
            q = session.query(cls)
            q = q.filter(cls.shape_id == pattern_id)
            # TODO q.filter(cls.agency_id == agency_id)
            ret_val = q.one()
        except Exception as e:
            log.info(e)
        return ret_val

    @classmethod
    def get_geometry_geojson(cls, session, pattern_id, agency=None):
        """
        :returns a geojson object for the pattern geometry (should be of type:LineString)
        """
        ret_val = None
        try:
            #import pdb; pdb.set_trace()
            pattern = cls.query_pattern(session, pattern_id, agency)
            dblist = session.query(func.st_asgeojson(pattern.geom)).one()
            ret_val = eval(dblist[0]) # query result comes back as list with one 'string' entry -- eval converts to dict
        except Exception as e:
            log.info(e)
        return ret_val

    @classmethod
    def get_geometry_encoded(cls, session, pattern_id, agency=None):
        """
        :returns a dict with 2 fields ... google encoded points and length
        """
        ret_val = {
            'points': None,
            'length': 0
        }

        try:
            #import pdb; pdb.set_trace()
            pattern = cls.query_pattern(session, pattern_id, agency)
            points = session.query(func.st_asencodedpolyline(pattern.geom)).one()
            length = session.query(func.st_npoints(pattern.geom)).one()
            ret_val['length'] = length[0]
            ret_val['points'] = points[0]
        except Exception as e:
            log.info(e)
        return ret_val
