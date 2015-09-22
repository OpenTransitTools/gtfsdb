from sqlalchemy import Column, Integer, Sequence, String, ForeignKey
from sqlalchemy.orm import relationship

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.stop import Stop

class Transfer(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'transfers.txt'

    __tablename__ = 'gtfs_transfers'

    transfer_id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    from_stop_id = Column(String(255), ForeignKey(Stop.__tablename__+'.stop_id'))
    to_stop_id = Column(String(255), ForeignKey(Stop.__tablename__+'.stop_id'))
    transfer_type = Column(Integer, default=0)
    min_transfer_time = Column(Integer)

    from_stop = relationship('Stop', primaryjoin='Stop.stop_id==Transfer.from_stop_id')
    to_stop = relationship('Stop', primaryjoin='Stop.stop_id==Transfer.to_stop_id')
