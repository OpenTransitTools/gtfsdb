import os
import inspect
from gtfsdb import Database
from .scripts import get_args
from .util import get_csv, do_sql

import logging
log = logging.getLogger(__name__)

#this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def shared_stops_parser(stops_csv_file, db, cmp="TRIMET"):
    """
    simple shared stops read
    reads shared_stops.csv, and match up with agency id from feed_agency.csv
    format:  feed_id:agency_id:stop_id,...
    example: "TRIMET:TRIMET:7646,CTRAN:C-TRAN:5555,RIDECONNECTION:133:876575"
    """
    ret_val = {}
    tm = 'TRIMET:TRIMET'

    def nearest(feed_id, cmp, stop_id, dist):
        sql = "select * from {}.stops r where st_dwithin(r.geom, (select t.geom from {}.stops t where stop_id = '{}'), {})".format(feed_id, cmp, stop_id, dist)
        return do_sql(db, sql)

    stop_dict = get_csv(stops_csv_file)
    for s in stop_dict:
        stop_id = s['TRIMET_ID']
        feed_id = s['FEED_ID']

        result = nearest(feed_id, cmp, stop_id, 0.00013)
        if result is not None:
            if not result:
                result = nearest(feed_id, cmp, stop_id, 0.00021)
                if not result:
                    result = nearest(feed_id, cmp, stop_id, 0.00033)
                    if not result:
                        result = nearest(feed_id, cmp, stop_id, 0.00055)
                
            if not result or len(result) > 1:
                print("{}:{} = {}".format(feed_id, stop_id, result))

        faid = "{}:{}".format(feed_id, stop_id)
        if ret_val.get(stop_id):
            m = ret_val.get(stop_id)
            ret_val[stop_id] = "{},{}".format(m, faid)
        else:
            ret_val[stop_id] = faid
    #print(ret_val)


def db_post_process():
    #import pdb; pdb.set_trace()
    args, kwargs = get_args()
    db = Database(**kwargs)
    shared_stops_parser(args.file, db)

    """
    with db.engine.connect() as conn:
        t = text("select * from rideconnection.stops r where st_dwithin(r.geom, (select t.geom from trimet.stops t where stop_id = '35'), 0.0001)")
        result = conn.execute(t).fetchall()
    """

    """
    """