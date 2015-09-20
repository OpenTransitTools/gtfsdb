__author__ = 'rhunter'
import pickle
import os.path
from gtfsdb.import_api.gtfs_exchange import GTFSExchange
from pkg_resources import resource_filename

'''
{
    'dataexchange_id': "",
    'file_url': "URL",
    'file_name': "Filename",
    'file_checksum' : "MD5Has"
    'date_added': 1213154234.0
}


'''

def gtfs_source_list():
    data_dir = resource_filename('gtfsdb', 'data')
    src_file = os.path.join(data_dir, 'url_list.pkl')
    data_feed = pickle.load(open(src_file, 'rb'))
    file_feed = []
    for f in data_feed:
        if f:
            datafile = GTFSExchange.recent_file(f['datafiles'])
            file_feed.append({ 'file_url': datafile['file_url'] })
    return file_feed

