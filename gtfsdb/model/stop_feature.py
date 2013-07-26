from sqlalchemy import Column, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb.model.base import Base


__all__ = ['StopFeatureType', 'StopFeature']


class StopFeatureType(Base):
    __tablename__ = 'stop_feature_type'

    feature_type = Column(String(50), primary_key=True)
    feature_name = Column(String(255))


class StopFeature(Base):
    __tablename__ = 'stop_features'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    stop_id = Column(
        String(255), ForeignKey('stops.stop_id'), index=True, nullable=False)
    feature_type = Column(String(50),
        ForeignKey('stop_feature_type.feature_type'),
        index=True, nullable=False)

    stop_feature_type = relationship('StopFeatureType')
