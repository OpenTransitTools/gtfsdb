__author__ = 'rhunter'

import unittest
import os
import mock

from datetime import datetime

from gtfsdb.api import get_feeds_from_directory

class TestAPI(unittest.TestCase):
    @mock.patch('gtfsdb.api.getpass')
    @mock.patch('gtfsdb.api.datetime')
    def test_get_zip_feeds(self, mock_utc_now, mock_getpass):
        fake_time = datetime(2015, 9, 28, 12, 27)
        mock_utc_now.utcnow.return_value = fake_time
        mock_getpass.getuser.return_value = 'feeduser'
        feed_dir = os.path.join(os.path.dirname(__file__), 'data/zip_test_dir')
        feed_files = get_feeds_from_directory(feed_dir)
        self.assertEqual(3, len(feed_files))
        for feed_file in feed_files:
            self.assertEqual(feed_file.uploaded_by_user, 'censio-feeduser')
            self.assertEqual(feed_file.date_added, fake_time)
            self.assertEqual(feed_file.description, 'Manual Upload')


