import logging

from gtfsdb import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

log = logging.getLogger(__file__)


class Database(object):

    def __init__(self, **kwargs):
        """
        keyword arguments:
            is_geospatial: if database supports geo functions
            schema: database schema name
            tables: limited list of tables to load into database
            url: SQLAlchemy database url
        """
        self.tables = kwargs.get('tables', None)
        self.url = kwargs.get('url', config.DEFAULT_DATABASE_URL)
        self.schema = kwargs.get('schema', config.DEFAULT_SCHEMA)
        self.is_geospatial = kwargs.get('is_geospatial', config.DEFAULT_IS_GEOSPATIAL)
        self.sorted_class_names = config.SORTED_CLASS_NAMES

    @property
    def classes(self):
        subclasses = self.get_base_subclasses()
        if self.tables:
            ret_val = [c for c in subclasses if c.__tablename__ in self.tables]
        else:
            ret_val = subclasses
        return ret_val

    @property
    def sorted_classes(self):
        classes = []
        for class_name in self.sorted_class_names:
            cls = next((c for c in self.classes if c.__name__ == class_name), None)
            if cls:
                classes.append(cls)
        return classes

    @classmethod
    def get_base_subclasses(cls):
        from gtfsdb.model.base import Base
        return Base.__subclasses__()

    @property
    def metadata(self):
        from gtfsdb.model.base import Base
        return Base.metadata

    @classmethod
    def factory(cls, **kwargs):
        db = cls(**kwargs)
        if kwargs.get('create'):
            db.create()
        return db

    @classmethod
    def factory_from_cmdline(cls, args):
        kwargs = vars(args)
        return cls.factory(**kwargs)

    def load_tables(self, **kwargs):
        """ load the sorted classes """
        # import pdb; pdb.set_trace()
        for cls in self.sorted_classes:
            log.info("load {}".format(cls.__name__))
            cls.load(self, **kwargs)

    def create(self):
        """Drop/create GTFS database"""
        for cls in self.sorted_classes:
            log.debug("create table: {0}".format(cls.__table__))
            try:
                cls.__table__.drop(self.engine, checkfirst=True)
            except:
                log.info("NOTE: couldn't drop table")
            cls.__table__.create(self.engine)

    @property
    def dialect_name(self):
        return self.engine.url.get_dialect().name

    @property
    def is_geospatial(self):
        return self._is_geospatial

    @is_geospatial.setter
    def is_geospatial(self, val):
        self._is_geospatial = val
        for cls in self.classes:
            if val and hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()

    @property
    def is_postgresql(self):
        return 'postgres' in self.dialect_name

    @property
    def is_sqlite(self):
        return 'sqlite' in self.dialect_name

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, val):
        self._schema = val

        # TODO ... move to create() method
        try:
            if self._schema:
                from sqlalchemy.schema import CreateSchema
                self.engine.execute(CreateSchema(self._schema))
        except Exception as e:
            log.info("NOTE: couldn't create schema {0} (schema might already exist)\n{1}".format(self._schema, e))

        for cls in self.classes:
            cls.__table__.schema = val

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, val):
        self._url = val
        self.engine = create_engine(val)
        if self.is_sqlite:
            self.engine.connect().connection.connection.text_factory = str
        session_factory = sessionmaker(self.engine)
        self.session = scoped_session(session_factory)
