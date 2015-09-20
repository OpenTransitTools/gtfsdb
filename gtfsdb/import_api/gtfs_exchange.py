import json
from gtfsdb.import_api.common import get_url
from pkg_resources import resource_filename
import os.path

__author__ = 'rhunter'


class GTFSExchange(object):
    def __init__(self, offline=True, src_name='gtfs_db_1442779052.json'):
        self.offline = offline
        if offline:
            data_dir = resource_filename('gtfsdb', 'data')
            src_file = os.path.join(data_dir, src_name)
            f = json.load(open(src_file, 'r'))
            self.agency_list = f['agencies']
            self.details = f['details']

    @staticmethod
    def recent_file(datafiles):
        if datafiles and len(datafiles) > 0:
            return max(datafiles, key=lambda k: k['date_added'])

    def get_gtfs_agencies(self):
        if self.offline:
            return self.agency_list
        else:
            return get_url('http://www.gtfs-data-exchange.com/api/agencies')

    def get_gtfs_agency_details(self, agency):
        agency_id = agency['dataexchange_id']
        if self.offline:
            return self.details[agency_id]
        else:
            return get_url('http://www.gtfs-data-exchange.com/api/agency?agency={}'.format(agency_id))

    def get_most_recent_file(self, agency):
        full_details = self.get_gtfs_agency_details(agency)
        return {'name': agency['name'], 'file': self.recent_file(full_details['datafiles'])}
