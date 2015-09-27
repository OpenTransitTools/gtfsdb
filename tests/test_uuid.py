__author__ = 'rhunter'


import unittest
import libuuid
import uuid

class TestUUID(unittest.TestCase):
    def test_uuid_4(self):
        test_id = '4ba8f248-bb02-4d30-b9fa-dd03dc475081'
        fast_uuid = libuuid.FastUUID(test_id)
        slow_uuid = uuid.UUID(test_id)
        self.assertEqual(test_id, str(fast_uuid))
        self.assertEqual(test_id, str(slow_uuid))



