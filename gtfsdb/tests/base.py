from gtfsdb import util
from gtfsdb.model.db import Database
from gtfsdb.api import database_load

from pkg_resources import resource_filename
import os
import logging
log = logging.getLogger(__name__)


def get_test_directory_path():
    """ will return current path ... tries to handle c:\\ windows junk """
    path = resource_filename('gtfsdb', 'tests')
    path = path.replace('c:\\', '/').replace('\\', '/')
    return path


def get_gtfs_file_uri(gtfs_file):
    """ will send back proper file:////blah/test_file.zip """
    dir_path = get_test_directory_path()
    file_uri = "file://{0}".format(os.path.join(dir_path, gtfs_file))
    file_uri = file_uri.replace('\\', '/')
    return file_uri


def load_sqlite(db_name=None, gtfs_name='multi-date-feed.zip'):
    # import pdb; pdb.set_trace()
    gtfs_uri = get_gtfs_file_uri(gtfs_name)
    url = util.make_temp_sqlite_db_uri(db_name)
    db = database_load(gtfs_uri, url=url, current_tables=True)
    return db


def load_pgsql(url, schema="current_test"):
    """ To run this test, do the following:
     x) bin/test  gtfsdb.tests.test_current

     You might also have to do the following:
     a) emacs setup.py - uncomment install_requires='psycopg2'
     b) buildout  # need psychopg2 in bin/test script
     c) comment out "#SKIP_TESTS = True" below
     d) psql -d postgres -c "CREATE DATABASE test WITH OWNER ott;"
     e) bin/test gtfsdb.tests.test_current
    """
    #import pdb; pdb.set_trace()
    gtfs_uri = get_gtfs_file_uri('multi-date-feed.zip')
    db = database_load(gtfs_uri, url=url, schema=schema, is_geospatial=True, current_tables=True)
    return db


def get_pg_db(url, schema='trimet'):
    db = Database(url=url, schema=schema, is_geospatial=True, current_tables=True)
    return db


def print_list(list):
    for i in list:
        print(i.__dict__)


def check_counts(list1, list2, id='stop_id'):
    """ check first that lists both have content; then chekc that either the lists are diff in size or content """
    ret_val = False
    #print_list(list1)
    #print_list(list2)
    if len(list1) > 0 and len(list2) > 0:
        if len(list1) != len(list2):
            ret_val = True
        else:
            for i, e1 in enumerate(list1):
                v1 = getattr(e1, id)
                v2 = getattr(list2[i], id)
                if v1 != v2:
                    ret_val = True
                    #print("{} VS. {}".format(v1, v2))
                    #print("{} VS. {}".format(e1.stop.stop_name, list2[i].stop_name))
                    break
    return ret_val
