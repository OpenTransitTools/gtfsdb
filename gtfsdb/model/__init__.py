__import__('pkg_resources').declare_namespace(__name__)

from gtfsdb.model.base import Base
from sqlalchemy.ext.declarative import declarative_base


DeclarativeBase = declarative_base(cls=Base)

required_files = ['agency.txt', 'stops.txt', 'routes.txt',
                  'trips.txt', 'stop_times.txt']
optional_files = ['calendar.txt', 'calendar_dates.txt', 'fare_attributes.txt',
                  'fare_rules.txt', 'shapes.txt', 'frequencies.txt',
                  'transfers.txt']
proposed_files = ['feed_info.txt', 'stop_features.txt']
files = required_files + optional_files + proposed_files

SRID = 4326


class ModelIterator:
    
    def __iter__(self):
        for cls in DeclarativeBase.__subclasses__():
            yield cls


def init(options):
    for cls in ModelIterator():
        cls.set_schema(options.schema)
        if options.geospatial and hasattr(cls, 'add_geometry_column'):
            cls.add_geometry_column()
