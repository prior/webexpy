import unittest2
from .. import timezone

class TimezoneTest(unittest2.TestCase):

    def setUp(self):
        pass

    def test_timezone_lookup(self):
        self.assertEquals(11, timezone.get_id('America/New_York'))
        self.assertEquals(11, timezone.get_id('US/Eastern'))

if __name__ == '__main__':
    unittest2.main()
