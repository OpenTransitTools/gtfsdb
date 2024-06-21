import json

from sqlalchemy import Column, String
from sqlalchemy.orm import deferred

from gtfsdb import config
from gtfsdb.model.base import Base


class Location(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'locations.geojson'

    __tablename__ = 'locations'

    id = Column(String(255), primary_key=True, index=True, nullable=False)
    region_color = Column(String(7), default=config.default_route_color)
    text_color = Column(String(7), default=config.default_text_color)
    region_desc = Column(String(1023))

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            from geoalchemy2 import Geometry
            cls.geom = deferred(Column(Geometry(srid=config.SRID)))

    @classmethod
    def make_record(cls, row):
        # import pdb; pdb.set_trace()
        if row.get('geometry') and hasattr(cls, 'geom'):
            row['geom'] = json.dumps(row['geometry'])
        return row
