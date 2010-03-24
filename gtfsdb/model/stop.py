from gtfsdb.model import DeclarativeBase, SRID
from geoalchemy import GeometryColumn, GeometryDDL, Point, WKTSpatialElement
from sqlalchemy import Column, Integer, Numeric, String


class Stop(DeclarativeBase):
    __tablename__ = 'stops'
    
    required_fields = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    optional_fields = ['stop_code', 'stop_desc', 'zone_id', 'stop_url',
                       'location_type', 'parent_station']

    stop_id = Column(String, primary_key=True)
    stop_code = Column(String)
    stop_name = Column(String, nullable=False)
    stop_desc = Column(String)
    stop_lat = Column(Numeric(12,9), nullable=False)
    stop_lon = Column(Numeric(12,9), nullable=False)
    zone_id = Column(String)
    stop_url = Column(String)
    location_type = Column(Integer, default=0)
    parent_station = Column(String)

    @classmethod
    def add_geometry_column(cls):
        cls.geom = GeometryColumn(Point(2))
        GeometryDDL(cls.__table__)
    
    @classmethod
    def add_geom_to_dict(cls, row):
        wkt = 'SRID=%s;POINT(%s %s)'% (SRID, row['stop_lon'], row['stop_lat'])
        row['geom'] = WKTSpatialElement(wkt)
