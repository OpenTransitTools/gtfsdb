from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, Integer, String


class Transfer(DeclarativeBase):
    __tablename__ = 'transfers'
    
    required_fields = ['from_stop_id', 'to_stop_id', 'transfer_type']
    optional_fields = ['min_transfer_time']

    from_stop_id = Column(String)
    to_stop_id = Column(String)
    transfer_type = Column(Integer, default=0)
    min_transfer_time = Column(Integer)
