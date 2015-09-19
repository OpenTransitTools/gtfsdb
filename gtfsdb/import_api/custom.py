__author__ = 'rhunter'
import pickle
import os.path
from gtfsdb.import_api.gtfs_exchange import recent_file

'''
{
    'dataexchange_id': "",
    'file_url': "URL",
    'file_name': "Filename",
    'file_checksum' : "MD5Has"
    'date_added': 1213154234.0
}


'''

def gtfs_source_list(pickle_file_location):
    data_feed = pickle.load(open(pickle_file_location, 'rb'))
    for f in data_feed:
        if f:
            inpu = recent_file(f['datafiles'])
            print inpu['agencies']


if __name__ == '__main__':
    gtfs_source_list(os.path.expanduser('data/file_list.pkl'))