from sqlalchemy import Column, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


__all__ = ['StopFeatureType', 'StopFeature']


class StopFeatureType(Base):
    datasource = config.DATASOURCE_LOOKUP
    filename = 'stop_feature_type.txt'

    __tablename__ = 'stop_feature_type'

    feature_type = Column(String(50), primary_key=True)
    feature_name = Column(String(255))


class StopFeature(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_features.txt'

    __tablename__ = 'stop_features'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    stop_id = Column(String(255), index=True, nullable=False)
    feature_type = Column(String(50), index=True, nullable=False)

    stop_feature_type = relationship('StopFeatureType',
        primaryjoin='StopFeature.feature_type==StopFeatureType.feature_type',
        foreign_keys='(StopFeature.feature_type)',
        uselist=False, viewonly=True)
