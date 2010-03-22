from gtfsdb.model import DeclarativeBase
from sqlalchemy import Column, Integer, String


class Trip(DeclarativeBase):
    __tablename__ = 'trips'

    required_fields = ['route_id', 'service_id', 'trip_id']
    optional_fields = ['trip_headsign', 'trip_short_name', 'direction_id',
                       'block_id', 'shape_id']
    proposed_fields = ['trip_bikes_allowed']

    route_id = Column(String)
    service_id = Column(String)
    trip_id = Column(String, primary_key=True)
    trip_headsign = Column(String)
    trip_short_name = Column(String)
    direction_id = Column(Integer)
    block_id = Column(String)
    shape_id= Column(String)
