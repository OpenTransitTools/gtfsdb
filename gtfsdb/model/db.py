from sqlalchemy import create_engine

from .base import Base


class Database(object):

    def __init__(self, url, schema=None, is_geospatial=False):
        self.url = url
        self.schema = schema
        self.is_geospatial = is_geospatial
        for cls in Base.__subclasses__():
            cls.set_schema(schema)
            if is_geospatial and hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()
        self.engine = create_engine(url)

    def create(self):
        """Create GTFS database"""
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
