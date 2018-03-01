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