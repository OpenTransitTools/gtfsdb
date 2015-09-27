from sqlalchemy import Column, Sequence, Index
from sqlalchemy.types import Integer, Numeric, String
from sqlalchemy.orm import relationship

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


Index('ix_gtfs_fare_attributes_fare_id', FareAttribute.fare_id, postgresql_using='hash')


class FareRule(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'fare_rules.txt'

    __tablename__ = 'gtfs_fare_rules'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    fare_id = Column(GUID(), nullable=False)
    route_id = Column(GUID(), nullable=False)
    origin_id = Column(GUID())
    destination_id = Column(GUID())
    contains_id = Column(GUID())
    service_id = Column(GUID())

    fare_attributes = relationship('FareAttribute', primaryjoin='FareRule.fare_id==FareAttribute.fare_id',
                                   foreign_keys='(FareRule.fare_id)', backref='fare_rule', uselist=True,
                                   cascade='delete')

Index('ix_gtfs_fare_rule_fare_id', FareRule.fare_id, postgresql_using='hash')
Index('ix_gtfs_fare_rule_route_id', FareRule.route_id, postgresql_using='hash')
Index('ix_gtfs_fare_rule_origin_id', FareRule.origin_id, postgresql_using='hash')
Index('ix_gtfs_fare_rule_destination_id', FareRule.destination_id, postgresql_using='hash')
Index('ix_gtfs_fare_rule_contains_id', FareRule.contains_id, postgresql_using='hash')
Index('ix_gtfs_fare_rule_service_id', FareRule.service_id, postgresql_using='hash')
