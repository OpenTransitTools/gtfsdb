"""
this is how to add more postgis ST_ functions to geoalchemy2
:see:
"""

from geoalchemy2 import Geometry
from geoalchemy2.functions import GenericFunction


class ST_ExteriorRing(GenericFunction):
    name = 'ST_ExteriorRing'
    type = Geometry


class ST_MakePolygon(GenericFunction):
    name = 'ST_MakePolygon'
    type = Geometry


class ST_Collect(GenericFunction):
    name = 'ST_Collect'
    type = Geometry


def point_intersects_geom(point, geom, buffer=0.0):
    """
    return true or false whether point is in / out of the geom
    """
    ret_val = False
    return ret_val


def point_distance_to_geom(point, geom):
    """
    return true or false whether point is in / out of the geom
    """
    ret_val = False
    return ret_val