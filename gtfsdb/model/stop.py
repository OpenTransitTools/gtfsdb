from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, Integer, Numeric, String
from geoalchemy import GeometryColumn, GeometryDDL, Point, WKTSpatialElement


class Stop(DeclarativeBase):
    __tablename__ = 'stops'
    required_fields = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    optional_fields = ['stop_code', 'stop_desc', 'zone_id', 'stop_url',
                       'location_type', 'parent_station']

    stop_id = Column(String, nullable=False)
    stop_code = Column(String)
    stop_name = Column(String)
    stop_desc = Column(String)
    stop_lat = Column(Numeric(12,9))
    stop_lon = Column(Numeric(12,9))
    zone_id = Column(String)
    stop_url = Column(String)
    location_type = Column(Integer, default=0)
    parent_station = Column(String)

    def __init__(self, *args, **kwargs):
        super(Stop, self).__init__(*args, **kwargs)
        if hasattr(self, 'geom'):
            self.geom = WKTSpatialElement(self.wkt)

    @classmethod
    def make_record(cls, row):
        row = cls.clean_dict(row)

        if row['stop_lon'] is not None and row['stop_lat'] is not None:
            z = WKTSpatialElement('SRID=%s;POINT(%s %s)'% (cls.get_srid(), row['stop_lon'], row['stop_lat']))
            row['geom'] = z
        return row

    @classmethod
    def add_geometry(cls):
        cls.geom = GeometryColumn(Point(2))
        GeometryDDL(cls.__table__)

    @property
    def wkt(self):
        s = 'SRID=%s;POINT(%s %s)'% (Stop.get_srid(), self.stop_lon, self.stop_lat)
        return s
