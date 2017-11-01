import os
from pkg_resources import resource_filename  # @UnresolvedImport
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from gtfsdb.api import database_load


class TestAPI(unittest.TestCase):

    def test_database_load(self):
        path = resource_filename('gtfsdb', 'tests')
        filename = 'file:///{0}'.format(os.path.join(path, 'sample-feed.zip'))
        database_load(filename, ignore_blocks=True)
