__author__ = 'rhunter'
import unittest
from gtfsdb.import_api.gtfs_exchange import GTFSExchange

class TestGTFSExchange(unittest.TestCase):

    def test_offline(self):
        gtfs_api = GTFSExchange()
        agencies = gtfs_api.get_gtfs_agencies()
        agency_detail = gtfs_api.get_gtfs_agency_details(agencies[0])
        file = gtfs_api.get_most_recent_file(agencies[0])
        pass

    def test_official_filter(self):
        gtfs_api = GTFSExchange()
        for agency in gtfs_api.get_gtfs_agencies(official_only=True):
            self.assertTrue(agency['is_official'])


