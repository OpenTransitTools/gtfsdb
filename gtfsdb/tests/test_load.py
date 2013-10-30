import os
from pkg_resources import resource_filename
import sys
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

from gtfsdb.scripts.load import load


class TestLoad(unittest.TestCase):

    def test_load(self):
        path = resource_filename('gtfsdb', 'tests')
        filename = 'file:///{0}'.format(os.path.join(path, 'sample-feed.zip'))
        load(filename)
