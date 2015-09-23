from sqlalchemy import Column, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID
import uuid


__all__ = ['StopFeature']


class StopFeature(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_features.txt'

    __tablename__ = 'stop_features'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    stop_id = Column(GUID(), nullable=False)
    feature_type = Column(String(50), nullable=False)
    feature_name = Column(String(255))
