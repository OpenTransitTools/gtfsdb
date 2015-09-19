__author__ = 'rhunter'

from gtfsdb.import_api.common import get_json_url


def get_agencies():
    return get_json_url('http://api.availabs.org/gtfs/agency/')


def get_routes(agency):
    return get_json_url('http://api.availabs.org/gtfs/agency/{}/routes'.format(agency['dataexchange_id']))

