from gtfsdb.model import DeclarativeBase, SRID

from geoalchemy import GeometryColumn, GeometryDDL, Point, LineString, WKTSpatialElement
from sqlalchemy import Column, Integer, Numeric, String


__all__ = ['Pattern', 'Shape']



class Pattern(DeclarativeBase):
    __tablename__ = 'patterns'

    shape_id = Column(String, primary_key=True)
    pattern_dist = Column(Numeric(20,10))

    @classmethod
    def add_geometry_column(cls):
        cls.geom = GeometryColumn(LineString(2))
        GeometryDDL(cls.__table__)

    @classmethod
    def get_filename(cls):
        return None

    @classmethod
    def load(cls, engine):
        print ' - %s' %(cls.__tablename__)



class Shape(DeclarativeBase):
    __tablename__ = 'shapes'
    
    required_fields = [
        'shape_id',
        'shape_pt_lat',
        'shape_pt_lon',
        'shape_pt_sequence'
    ]
    optional_fields = ['shape_dist_traveled']

    shape_id = Column(String, primary_key=True)
    shape_pt_lat = Column(Numeric(12,9))
    shape_pt_lon = Column(Numeric(12,9))
    shape_pt_sequence = Column(Integer, primary_key=True)
    shape_dist_traveled = Column(Numeric(20,10))

    @classmethod
    def add_geometry_column(cls):
        cls.geom = GeometryColumn(Point(2))
        GeometryDDL(cls.__table__)

    @classmethod
    def add_geom_to_dict(cls, row):
        wkt = 'SRID=%s;POINT(%s %s)' %(
            SRID,
            row['shape_pt_lon'],
            row['shape_pt_lat']
        )
        row['geom'] = WKTSpatialElement(wkt)
