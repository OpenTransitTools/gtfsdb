from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, Integer, Sequence, String


class Transfer(DeclarativeBase):
    __tablename__ = 'transfers'
    
    required_fields = ['from_stop_id', 'to_stop_id', 'transfer_type']
    optional_fields = ['min_transfer_time']

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    from_stop_id = Column(String)
    to_stop_id = Column(String)
    transfer_type = Column(Integer, default=0)
    min_transfer_time = Column(Integer)
