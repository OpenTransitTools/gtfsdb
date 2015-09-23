from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.orm import relationship
import uuid

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID

class Transfer(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'transfers.txt'

    __tablename__ = 'gtfs_transfers'

    id = Column(GUID(), default=uuid.uuid4, primary_key=True)
    from_stop_id = Column(GUID())
    to_stop_id = Column(GUID())
    transfer_type = Column(Integer, default=0)
    min_transfer_time = Column(Integer)

    from_stop = relationship('Stop', primaryjoin='Stop.stop_id==Transfer.from_stop_id', foreign_keys='(Stop.stop_id)')
    to_stop = relationship('Stop', primaryjoin='Stop.stop_id==Transfer.to_stop_id', foreign_keys='(Stop.stop_id)')
