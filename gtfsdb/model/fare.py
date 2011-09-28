from sqlalchemy import Column, ForeignKey, Index, Sequence
from sqlalchemy.types import Integer, Numeric, String

from .base import Base


__all__ = ['FareAttribute', 'FareRule']


class FareAttribute(Base):
    __tablename__ = 'fare_attributes'

    required_fields = [
        'fare_id',
        'price',
        'currency_type',
        'payment_method',
        'transfers'
    ]
    optional_fields = ['transfer_duration']
    proposed_fields = ['agency_id']

    fare_id = Column(String, primary_key=True)
    price = Column(Numeric(10,2), nullable=False)
    currency_type = Column(String, nullable=False)
    payment_method = Column(Integer, nullable=False)
    transfers = Column(Integer)
    transfer_duration = Column(Integer)


class FareRule(Base):

    __tablename__ = 'fare_rules'

    required_fields = ['fare_id']
    optional_fields = ['route_id', 'origin_id', 'destination_id', 'contains_id']
    proposed_fields = ['service_id']

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    fare_id = Column(String, ForeignKey(FareAttribute.fare_id), nullable=False)
    route_id = Column(String)
    origin_id = Column(String)
    destination_id = Column(String)
    contains_id = Column(String)
    service_id = Column(String)

Index('%s_ix1' %(FareRule.__tablename__), FareRule.fare_id)
