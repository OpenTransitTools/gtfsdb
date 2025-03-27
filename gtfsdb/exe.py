import os
import inspect
from gtfsdb import Database
from .scripts import get_args
from .util import get_csv, do_sql

import logging
log = logging.getLogger(__name__)


NOT_FOUND = "not found"
INCHES_AWAY = "inches away"
FEET_AWAY = "feet away"
YARDS_AWAY = "yards away"
BLOCKS_AWAY = "blocks away"

IGNORE_AGENCIES = ['CANBY', 'CCRIDER', 'CAT', 'YAMHILL']


#this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# https://maps.trimet.org/ti/index/patterns/trip/TRIMET:14389120/geometry/geojson

def nearest(db, feed_id, stop_id, dist, src_feed_id, table="STOPS"):
    sql = "select * from {}.{} stop where st_dwithin(stop.geom, (select t.geom from {}.stops t where stop_id = '{}'), {})".format(feed_id, table, src_feed_id, stop_id, dist)
    #print(sql)
    return do_sql(db, sql)


def mk_feed_stop(feed_id, stop_id):
    return "{}:{}".format(feed_id, stop_id)


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
        

def get_nearest_record(db, feed_id, stop_id, dist, dist_desc, src_feed_id, ignore_seen_filter=False):
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

            if rec and (ignore_seen_filter or not is_already_seen(rec)):
                share.append(rec)

        if share:
            ret_val = { 
                'src': src,
                'dist': dist,
                'dist_desc': dist_desc,
                'share': share
            }


    return ret_val


def shared_stops_parser(stops_csv_file, db, src_feed_id="TRIMET"):
    """
    simple shared stops read
    reads shared_stops.csv, and match up with agency id from feed_agency.csv
    format:  feed_id:agency_id:stop_id,...
    example: "TRIMET:TRIMET:7646,CTRAN:C-TRAN:5555,RIDECONNECTION:133:876575"
    """
    ret_val = {
        'src': [],
        NOT_FOUND: [],
        INCHES_AWAY: [],
        FEET_AWAY: [],
        YARDS_AWAY: [],
        BLOCKS_AWAY: []
    }

    stop_dict = get_csv(stops_csv_file)
    for s in stop_dict:

        # step 1: get stop_id we're looking for in given feed_id
        stop_id = s['TRIMET_ID']
        feed_id = s['FEED_ID']

        # step 2: skip unsupported agencies
        if feed_id in IGNORE_AGENCIES:
            continue

        # step 3: save off this shared stop (reporting)
        ret_val['src'].append(s)

        # step 4: progressively find nearest stops based on distance
        result = get_nearest_record(db, feed_id, stop_id, 0.00013, INCHES_AWAY, src_feed_id, True)
        if result:
            ret_val[INCHES_AWAY].append(result)
        else:
            result = get_nearest_record(db, feed_id, stop_id, 0.00033, FEET_AWAY, src_feed_id, True)
            if result:
                ret_val[FEET_AWAY].append(result)
            else:
                result = get_nearest_record(db, feed_id, stop_id, 0.00066, YARDS_AWAY, src_feed_id, True)
                if result:
                    ret_val[YARDS_AWAY].append(result)
                else:
                    result = get_nearest_record(db, feed_id, stop_id, 0.0055, BLOCKS_AWAY, src_feed_id)
                    if result:
                        ret_val[BLOCKS_AWAY].append(result)
                    else:
                        ret_val[NOT_FOUND].append({'feed_stop': mk_feed_stop(src_feed_id, stop_id), 'share': feed_id})
    return ret_val


def generate_report(ss):
    url = "https://rtp.trimet.org/rtp/#/schedule"

    print("There are {} shared stops defined in TRANS.".format(len(ss['src'])))

    print("\nCould not find a matching stop for the following ({}):".format(len(ss[NOT_FOUND])))
    for s in ss[NOT_FOUND]:
        print("   {}: {}/{}".format(s['share'], url, s['feed_stop']))

    for d in [BLOCKS_AWAY, YARDS_AWAY, FEET_AWAY, INCHES_AWAY]:
        print("\nThese stops are {} from the target stop ({}):".format(d, len(ss[d])))
        for s in ss[d]:
            print("   {}: {}/{}".format(s['share'], url, s['src']))


def db_post_process():
    args, kwargs = get_args()
    db = Database(**kwargs)
    ss = shared_stops_parser(args.file, db)
    generate_report(ss)