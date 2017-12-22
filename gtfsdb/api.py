from gtfsdb import Database, GTFS


def database_load(filename, **kwargs):
    """
    Basic API to load a GTFS zip file into a database

    arguments:
        filename: URL or local path to GTFS zip file

    keyword arguments:
        batch_size: record batch size for memory management
        is_geospatial: if database is support geo functions
        schema: database schema name
        tables: limited list of tables to load
        url: SQLAlchemy database url
    """
    db = Database(**kwargs)
    db.create()
    gtfs = GTFS(filename)
    gtfs.load(db, **kwargs)
    return db
