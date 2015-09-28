__author__ = 'rhunter'
import os
import time
import tempfile
import zipfile
from contextlib import closing

import testing.postgresql

from gtfsdb.model.db import Database
from gtfsdb.api import database_load
from gtfsdb import config
import itertools

root_dir = os.path.dirname(__file__)

def run_import(url, **kwargs):
    db = Database(url=postgresql.url())
    db.create()
    database_load(os.path.join(root_dir, 'data/performance-dataset.zip'), db_url=url, **kwargs)
    db.drop_all()

def unzip_file(file_path):
    temp_dir = tempfile.mkdtemp()
    with closing(zipfile.ZipFile(file_path)) as z:
        z.extractall(temp_dir)
    return temp_dir


with testing.postgresql.Postgresql() as postgresql:
    db = Database(url=postgresql.url())
    db.engine.execute('create extension postgis;')
    db.engine.execute('create extension postgis_topology;')

    run_x = 3
    start_time = time.time()

    batch_size = config

    #batch_sizes = [1000, 5000, 10000]
    batch_sizes = [10000]
    db_threads = [1]#,5,10]

    result_list = []
    for batch_size in batch_sizes:
        for db_th in db_threads:
            t_start = time.time()
            run_import(postgresql.url(), batch_size=batch_size, db_threads=db_th)
            res = "Batch size: {} Threads: {} Took {} sec".format(batch_size, db_th, time.time()-t_start)
            print res
            result_list.append(res)

    print "Took: {} tor run {} times".format(time.time() - start_time, run_x)
    for res in result_list:
        print res

