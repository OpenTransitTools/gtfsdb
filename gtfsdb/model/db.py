from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database(object):

    def __init__(self, url, schema=None, is_geospatial=False):
        self.url = url
        self.schema = schema
        self.is_geospatial = is_geospatial
        for cls in self.classes:
            cls.__table__.schema = schema
            if is_geospatial and hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()
        self.engine = create_engine(url)

    @property
    def classes(self):
        from gtfsdb.model.base import Base
        return Base.__subclasses__()

    @property
    def metadata(self):
        from gtfsdb.model.base import Base
        return Base.metadata

    def create(self):
        """Create GTFS database"""
        self.metadata.drop_all(bind=self.engine)
        self.metadata.create_all(bind=self.engine)

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session
