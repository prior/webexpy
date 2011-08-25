import unittest2
import datetime
import pprint
import pytz

from webex.timezone import WebExTimezone, WEBEX_TIMEZONE_DATA

class WebExTimezoneTest(unittest2.TestCase):

    def test_tzinfo_existence(self):
        for id, webexlabel, tzlabel in WEBEX_TIMEZONE_DATA:
            if tzlabel is not None:
                self.assertEquals(id,WebExTimezone(tzinfo=WebExTimezone(id).tzinfo).id)

    def test_localize_new_naive_datetime(self):
        for month in xrange(12): # to test dst and std times
            expected = pytz.timezone('America/New_York').localize(datetime.datetime(2011,month+1,1))
            actual = WebExTimezone(11).localize_new_naive_datetime(2011,month+1,1)
            self.assertEquals(expected, actual)

    def test_localize_naive_datetime(self):
        for month in xrange(12): # to test dst and std times
            naive_datetime = datetime.datetime(2011,month+1,1)
            expected = pytz.timezone('America/New_York').localize(datetime.datetime(2011,month+1,1))
            actual = WebExTimezone(11).localize_naive_datetime(naive_datetime)
            self.assertEquals(expected, actual)

    def test_from_localized_datetime(self):
        for month in xrange(12): # to test dst and std times
            local_datetime = pytz.timezone('America/New_York').localize(datetime.datetime(2011,month+1,1))
            webex_timezone = WebExTimezone.from_localized_datetime(local_datetime)
            self.assertEquals(11, webex_timezone.id)

if __name__ == '__main__':
    unittest2.main()
