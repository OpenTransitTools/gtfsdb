__author__ = 'rhunter'
import os
import time

import testing.postgresql

from gtfsdb.model.db import Database
from gtfsdb.api import database_load
from gtfsdb.config import batch

def run_import(url):
    db = Database(url=postgresql.url())
    db.create()
    root_dir = os.path.dirname(__file__)
    database_load(os.path.join(root_dir, 'data/performance-dataset.zip'), db_url=url)
    db.drop_all()

with testing.postgresql.Postgresql() as postgresql:
    db = Database(url=postgresql.url())
    db.engine.execute('create extension postgis;')
    db.engine.execute('create extension postgis_topology;')

    run_x = 3
    start_time = time.time()

    for _ in range(run_x):
        t_start = time.time()
        run_import(postgresql.url())
        print "Batch size: {} Took {} sec".format(batch.DEFAULT_BATCH_SIZE, time.time()-t_start)
        batch.DEFAULT_BATCH_SIZE = batch.DEFAULT_BATCH_SIZE * 10

    print "Took: {} tor run {} times".format(time.time() - start_time, run_x)

