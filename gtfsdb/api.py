from gtfsdb import Database, GTFS


def database_load(filename, **kwargs):
    '''Basic API to load a GTFS zip file into a database

    arguments:
        filename: URL or local path to GTFS zip file

    keyword arguments:
        batch_size: record batch size for memory management
        database_url: SQLAlchemy database url
        schema: database schema name
        is_geospatial: if database is support geo functions
    '''

    db = Database(**kwargs)
    db.create()
    gtfs = GTFS(filename)
    gtfs.load(db, **kwargs)
