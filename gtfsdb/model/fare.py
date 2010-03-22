from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, Integer, Numeric, String


__all__ = ['FareAttribute', 'FareRule']


class FareAttribute(DeclarativeBase):
    __tablename__ = 'fare_attributes'

    required_fields = ['fare_id', 'price', 'currency_type', 'payment_method',
        'transfers']
    optional_fields = ['transfer_duration']
    proposed_fields = ['agency_id']

    fare_id = Column(String)
    price = Column(Numeric(10,2))
    currency_type = Column(String)
    payment_method = Column(Integer)
    transfers = Column(Integer)
    transfer_duration = Column(Integer)


class FareRule(DeclarativeBase):

    __tablename__ = 'fare_rules'

    required_fields = ['fare_id']
    optional_fields = ['route_id', 'origin_id', 'destination_id', 'contains_id']
    proposed_fields = ['service_id']

    fare_id = Column(String)
    route_id = Column(String)
    origin_id = Column(String)
    destination_id = Column(String)
    contains_id = Column(String)
    service_id = Column(String)
