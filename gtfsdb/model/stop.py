from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import relationship

from gtfsdb.config import config
from gtfsdb.model.base import Base


class Stop(Base):
    __tablename__ = 'stops'

    stop_id = Column(String(255), primary_key=True, nullable=False)
    stop_code = Column(String(50))
    stop_name = Column(String(255), nullable=False)
    stop_desc = Column(String(255))
    stop_lat = Column(Numeric(12, 9), nullable=False)
    stop_lon = Column(Numeric(12, 9), nullable=False)
    zone_id = Column(String(50))
    stop_url = Column(String(255))
    location_type = Column(Integer, index=True, default=0)
    parent_station = Column(String(255))
    stop_timezone = Column(String(50))
    wheelchair_boarding = Column(Integer, default=0)
    platform_code = Column(String(50))

    stop_features = relationship('StopFeature')
    stop_times = relationship('StopTime')

    @classmethod
    def add_geometry_column(cls):
        from geoalchemy import GeometryColumn, GeometryDDL, Point

        cls.geom = GeometryColumn(Point(2))
        GeometryDDL(cls.__table__)

    @classmethod
    def add_geom_to_dict(cls, row):
        try:
            from geoalchemy import WKTSpatialElement
            wkt = 'SRID=%s;POINT(%s %s)' % (
                config.get('DEFAULT', 'SRID'),
                row['stop_lon'],
                row['stop_lat']
            )
            row['geom'] = WKTSpatialElement(wkt)
        except ImportError:
            pass
