from gtfsdb.model import SRID
from geoalchemy import GeometryColumn, GeometryDDL, Point, WKTSpatialElement
from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric, Sequence, String

from .base import Base
from .stop import Stop

__all__ = ['StopFeatureType', 'StopFeature']


class StopFeatureType(Base):
    __tablename__ = 'stop_feature_type'

    feature_type = Column(String, primary_key=True)
    feature_name = Column(String)


class StopFeature(Base):
    __tablename__ = 'stop_features'

    required_fields = ['stop_id', 'feature_type', 'stop_feature_type']
    optional_fields = []

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    stop_id = Column(String, ForeignKey(Stop.stop_id), nullable=False)
    feature_type = Column(String, ForeignKey(StopFeatureType.feature_type), nullable=False)

Index('%s_ix1' %(StopFeature.__tablename__), StopFeature.stop_id)
Index('%s_ix2' %(StopFeature.__tablename__), StopFeature.feature_type)
