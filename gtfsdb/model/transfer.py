from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Transfer(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'transfers.txt'

    __tablename__ = 'transfers'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    from_stop_id = Column(String(255))
    to_stop_id = Column(String(255))
    transfer_type = Column(Integer, index=True, default=0)
    min_transfer_time = Column(Integer)
