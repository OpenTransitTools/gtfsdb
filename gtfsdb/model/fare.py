from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, Numeric, String

from gtfsdb import config
from gtfsdb.model.base import Base


__all__ = ['FareAttribute', 'FareRule']


class FareAttribute(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'fare_attributes.txt'

    __tablename__ = 'fare_attributes'

    fare_id = Column(String(255), primary_key=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency_type = Column(String(255), nullable=False)
    payment_method = Column(Integer, nullable=False)
    transfers = Column(Integer)
    transfer_duration = Column(Integer)
    agency_id = Column(String(255))


class FareRule(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'fare_rules.txt'

    __tablename__ = 'fare_rules'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    fare_id = Column(String(255), index=True, nullable=False)
    route_id = Column(String(255))
    origin_id = Column(String(255))
    destination_id = Column(String(255))
    contains_id = Column(String(255))
    service_id = Column(String(255))
