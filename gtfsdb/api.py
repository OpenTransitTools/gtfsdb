from gtfsdb import Database, GTFS


def database_load(filename, database_url='sqlite://',
                  schema=None, is_geospatial=False):
    '''Basic API to load a GTFS zip file into a database

    arguments:
        filename: URL or local path to GTFS zip file
        database_url: SQLAlchemy database url
        schema: database schema name
        is_geospatial: if database is support geo functions
    '''
    db = Database(database_url, schema, is_geospatial)
    db.create()
    gtfs = GTFS(filename)
    gtfs.load(db)
