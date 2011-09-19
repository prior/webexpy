import unittest2
import datetime
import time
import calendar
from pprint import pprint
import pytz

from webex.timezone import Timezone, TIMEZONE_DATA

class TimezoneTest(unittest2.TestCase):

    def test_tzinfo_existence(self):
        for id, webexlabel, tzlabel in TIMEZONE_DATA:
            if tzlabel is not None:
                self.assertEquals(id,Timezone(tzinfo=Timezone(id).tzinfo).id)

    # HOLY FUCKING SHIT -- PYTHON DATE/TIME IS A COMPLETE CLUSTERFUCK
    def test_utc_conversions_across_all_timezones(self):
        for id, webexlabel, tzlabel in TIMEZONE_DATA:
            if tzlabel is not None:
                webex_tz = Timezone(id)
                for month in xrange(12): # to test dst and std times
                    expected_utc_seconds = calendar.timegm(datetime.datetime(2011,month+1,1,tzinfo=pytz.utc).timetuple())
                    actual = webex_tz.utc_timestamp_from_localized_datetime(webex_tz.localized_datetime_from_utc_timestamp(expected_utc_seconds))
                    self.assertEquals(expected_utc_seconds, actual)

    def test_localize_new_naive_datetime(self):
        for month in xrange(12): # to test dst and std times
            expected = pytz.timezone('America/New_York').localize(datetime.datetime(2011,month+1,1))
            pprint(expected)
            actual = Timezone(11).localize_new_naive_datetime(2011,month+1,1)
            self.assertEquals(expected, actual)

    def test_localize_naive_datetime(self):
        for month in xrange(12): # to test dst and std times
            naive_datetime = datetime.datetime(2011,month+1,1)
            expected = pytz.timezone('America/New_York').localize(datetime.datetime(2011,month+1,1))
            actual = Timezone(11).localize_naive_datetime(naive_datetime)
            self.assertEquals(expected, actual)

    def test_from_localized_datetime(self):
        for month in xrange(12): # to test dst and std times
            local_datetime = pytz.timezone('America/New_York').localize(datetime.datetime(2011,month+1,1))
            webex_timezone = Timezone.from_localized_datetime(local_datetime)
            self.assertEquals(11, webex_timezone.id)

if __name__ == '__main__':
    unittest2.main()
