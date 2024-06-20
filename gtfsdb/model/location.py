from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.types import String

from gtfsdb import config
from gtfsdb.model.base import Base


class Location(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'locations.geojson'

    __tablename__ = 'locations'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
