__author__ = 'rhunter'
from gtfsdb.import_api.common import get_url

def get_gtfs_agencies():
    return get_url('http://www.gtfs-data-exchange.com/api/agencies')


def get_gtfs_agency_details(agency):
    return get_url('http://www.gtfs-data-exchange.com/api/agency?agency={}'.format(agency['dataexchange_id']))

def get_most_recent_file(agency):
    full_details = get_gtfs_agency_details(agency)
    if full_details and len(full_details['datafiles']) > 0:
        return { 'name': agency['name'], 'file': max(full_details['datafiles'], key = lambda k: k['date_added'])}
