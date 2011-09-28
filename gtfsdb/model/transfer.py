from sqlalchemy import Column, Index, Integer, Sequence, String

from .base import Base


class Transfer(Base):
    __tablename__ = 'transfers'

    required_fields = ['from_stop_id', 'to_stop_id', 'transfer_type']
    optional_fields = ['min_transfer_time']

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    from_stop_id = Column(String)
    to_stop_id = Column(String)
    transfer_type = Column(Integer, default=0)
    min_transfer_time = Column(Integer)

Index('%s_ix1' %(Transfer.__tablename__), Transfer.transfer_type)
