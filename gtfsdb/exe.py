import os
import inspect
from gtfsdb import Database
from .scripts import get_args
from .util import get_csv, do_sql

import logging
log = logging.getLogger(__name__)

#this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# https://maps.trimet.org/ti/index/patterns/trip/TRIMET:14389120/geometry/geojson

def nearest(db, feed_id, stop_id, dist, src_feed_id, table="STOPS"):
    sql = "select * from {}.{} stop where st_dwithin(stop.geom, (select t.geom from {}.stops t where stop_id = '{}'), {})".format(feed_id, table, src_feed_id, stop_id, dist)
    #print(sql)
    return do_sql(db, sql)


def mk_feed_rec(feed_id, stop_id, agency_id="?"):
    return "{}:{}:{}".format(agency_id, feed_id, stop_id)


nearest_hits = {}
def is_already_seen(fs):
    global nearest_hits
    ret_val = False
    if fs in nearest_hits:
        ret_val = True
    nearest_hits[fs] = fs
    return ret_val
        

def get_nearest_record(db, feed_id, stop_id, dist, dist_desc, src_feed_id):
    ret_val = None

    from_current_stops = False
    from_stops_table = False

    result = nearest(db, feed_id, stop_id, dist, src_feed_id, "CURRENT_STOPS")
    if result:
        from_current_stops = True
    else:
        result = nearest(db, feed_id, stop_id, dist, src_feed_id, "STOPS")
        if result:
            from_stops_table = True

    if from_current_stops or from_stops_table:
        src = mk_feed_rec(src_feed_id, stop_id, src_feed_id)  # todo: call current for actual agency id (PSC or AT)

        share = []
        for r in result:
            if from_stops_table:
                rec = mk_feed_rec(feed_id, r[0])
            elif from_current_stops:
                rec = mk_feed_rec(feed_id, r[7], r[0])

            if rec and not is_already_seen(rec):
                share.append(rec)

        if share:
            ret_val = { 
                'src': src,
                'dist': dist,
                'dist_desc': dist_desc,
                'share': share
            }


    return ret_val


def append_result(result_hash, new_rec):
    pass


def shared_stops_parser(stops_csv_file, db, src_feed_id="TRIMET"):
    """
    simple shared stops read
    reads shared_stops.csv, and match up with agency id from feed_agency.csv
    format:  feed_id:agency_id:stop_id,...
    example: "TRIMET:TRIMET:7646,CTRAN:C-TRAN:5555,RIDECONNECTION:133:876575"
    """
    ret_val = {}

    stop_dict = get_csv(stops_csv_file)
    for s in stop_dict:
        stop_id = s['TRIMET_ID']
        feed_id = s['FEED_ID']

        result = get_nearest_record(db, feed_id, stop_id, 0.00013, "inches away", src_feed_id)
        if result:
            append_result(ret_val, result)
        else:
            result = get_nearest_record(db, feed_id, stop_id, 0.00033, "feet away", src_feed_id)
            if result:
                append_result(ret_val, result)
            else:
                result = get_nearest_record(db, feed_id, stop_id, 0.00066, "yards away", src_feed_id)
                if result:
                    append_result(ret_val, result)
                else:
                    result = get_nearest_record(db, feed_id, stop_id, 0.0055, "blocks away", src_feed_id)
                    if result:
                        append_result(ret_val, result)
                    else:
                        print(result)



def xshared_stops_parser(stops_csv_file, db, cmp="TRIMET"):
    ret_val = {}
    tm = 'TRIMET:TRIMET'

    stop_dict = get_csv(stops_csv_file)
    for s in stop_dict:
        stop_id = s['TRIMET_ID']
        feed_id = s['FEED_ID']

        result = nearest(db, feed_id, stop_id, 0.00013, cmp)
        if result is not None:
            if not result:
                result = nearest(db, feed_id, stop_id, 0.00021, cmp)
                if not result:
                    result = nearest(db, feed_id, stop_id, 0.00033, cmp)
                    if not result:
                        result = nearest(db, feed_id, stop_id, 0.00055, cmp)
                
            if not result or len(result) > 1:
                #import pdb; pdb.set_trace()
                #other_stop_id = result[0]
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
