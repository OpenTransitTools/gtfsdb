from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, Numeric, String
import uuid

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID


__all__ = ['FareAttribute', 'FareRule']


class FareAttribute(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'fare_attributes.txt'

    __tablename__ = 'gtfs_fare_attributes'

    fare_id = Column(GUID(), primary_key=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency_type = Column(String(255), nullable=False)
    payment_method = Column(Integer, nullable=False)
    transfers = Column(Integer)
    transfer_duration = Column(Integer)


class FareRule(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'fare_rules.txt'

    __tablename__ = 'gtfs_fare_rules'

    id = Column(GUID(), default=uuid.uuid4, primary_key=True)
    fare_id = Column(GUID(), nullable=False)
    route_id = Column(String(255))
    origin_id = Column(String(255))
    destination_id = Column(String(255))
    contains_id = Column(String(255))
    service_id = Column(String(255))
