from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, Integer, Numeric, String
from geoalchemy import GeometryColumn, GeometryDDL, Point, LineString, WKTSpatialElement


__all__ = ['Shape', 'Pattern']


class Shape(DeclarativeBase):
    __tablename__ = 'shapes'
    
    required_fields = ['shape_id', 'shape_pt_lat', 'shape_pt_lon',
                       'shape_pt_sequence']
    optional_fields = ['shape_dist_traveled']
    
    shape_id = Column(String, primary_key=True)
    shape_pt_lat = Column(Numeric(12,9))
    shape_pt_lon = Column(Numeric(12,9))
    shape_pt_sequence = Column(Integer, primary_key=True)
    shape_dist_traveled = Column(Numeric(20,10))

    def __init__(self, *args, **kwargs):
        super(Shape, self).__init__(*args, **kwargs)
        if hasattr(self, 'geom'):
            self.geom = WKTSpatialElement(self.wkt)

    @classmethod
    def add_geometry(cls):
        cls.geom = GeometryColumn(Point(2))
        GeometryDDL(cls.__table__)

    @property
    def wkt(self):
        s = 'SRID=%s;POINT(%s %s)'% (Shape.get_srid(), self.shape_pt_lon, self.shape_pt_lat)
        return s


class Pattern(DeclarativeBase):
    __tablename__ = 'patterns'
    
    shape_id = Column(String)
    pattern_dist = Column(Numeric(20,10))

    @classmethod
    def add_geometry(cls):
        cls.geom = GeometryColumn(LineString(2))
        GeometryDDL(cls.__table__)

    @classmethod
    def from_shape_points(cls, shape_id):
        pattern = cls()
        pattern.shape_id = shape_id
        return pattern
