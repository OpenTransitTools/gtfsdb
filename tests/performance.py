__author__ = 'rhunter'
import os
import time

import testing.postgresql

from gtfsdb.model.db import Database
from gtfsdb.api import database_load

def run_import(url):
        db = Database(url=postgresql.url())
        db.create()
        root_dir = os.path.dirname(__file__)
        database_load(os.path.join(root_dir, 'data/sample-feed.zip'), db_url=url)
        db.drop_all()

with testing.postgresql.Postgresql() as postgresql:
        db = Database(url=postgresql.url())
        db.engine.execute('create extension postgis;')
        db.engine.execute('create extension postgis_topology;')

        start_time = time.time()
        run_x = 50

        for _ in range(run_x):
                run_import(postgresql.url())

        print "Took: {} tor run {} times".format(time.time() - start_time, run_x)

