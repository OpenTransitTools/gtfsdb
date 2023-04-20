from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.types import String

from gtfsdb import config
from gtfsdb.model.base import Base


class Translation(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'translations.txt'

    __tablename__ = 'translations'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    table_name = Column(String(255), nullable=False)
    field_name = Column(String(255), nullable=False)
    language = Column(String(255), nullable=False)
    translation = Column(String(255), nullable=False)
    record_id = Column(String(255))
    record_sub_id = Column(String(255))
    field_value = Column(String(255))
