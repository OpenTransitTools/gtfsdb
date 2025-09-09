from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.types import String

from gtfsdb import config
from gtfsdb.model.base import Base


class Translation(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'translations.txt'

    __tablename__ = 'translations'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    table_name = Column(String(512), nullable=False)
    field_name = Column(String(512), nullable=False)
    language = Column(String(256), nullable=False)
    translation = Column(String(1024), nullable=False)
    record_id = Column(String(512))
    record_sub_id = Column(String(512))
    field_value = Column(String(1024))
