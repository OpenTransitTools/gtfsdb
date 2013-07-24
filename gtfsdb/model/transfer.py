from sqlalchemy import Column, Integer, Sequence, String

from gtfsdb.model.base import Base


class Transfer(Base):
    __tablename__ = 'transfers'

    required_fields = ['from_stop_id', 'to_stop_id', 'transfer_type']
    optional_fields = ['min_transfer_time']

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    from_stop_id = Column(String)
    to_stop_id = Column(String)
    transfer_type = Column(Integer, index=True, default=0)
    min_transfer_time = Column(Integer)
