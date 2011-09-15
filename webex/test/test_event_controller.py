import unittest2
import uuid
from datetime import datetime
from datetime import timedelta
import pytz
import pprint

from webex.webex import WebEx, WebExError
from webex.event import WebExEvent
from webex.event_controller import WebExEventController

import helper


# these integration tests are normally commented out so we don't incur their hits on every run of our test suite

UNITTEST_EVENT_DESCRIPTION = """This is a fake/dummy webinar event created by the unittest system to verify the WebEx systems are operational.  These events are normally deleted immediately after creation, but in the case that you are reading this, then something got screwed up.  Feel free to delete manually, however, we are very likely aware and on the case and will be cleaning up these fake events shortly."""

class EventControllerTest(unittest2.TestCase):

    @unittest2.skip('integration')
    def setUp(self):
        self.webex = helper.webex_from_test_credentials()
        self.event_controller = WebExEventController(self.webex)

    def test_list_events(self):
        new_events = [self.dummy_event(), self.dummy_event()]
        session_keys = [ev.session_key for ev in self.event_controller.list_events()]
        for ev in new_events:
            self.assertNotIn(ev.session_key, session_keys)
            self.event_controller.create_event(ev)
        session_keys = [ev.session_key for ev in self.event_controller.list_events()]
        for ev in new_events:
            self.assertIn(ev.session_key, session_keys)
            self.event_controller.delete_event(ev)

    def test_good_create(self):
        event = self.dummy_event()
        self.assertIsNone(event.session_key)
        self.assertEquals(event, self.event_controller.create_event(event))
        session_keys = [ev.session_key for ev in self.event_controller.list_events()]
        self.assertTrue(event.session_key)
        self.assertTrue(event.session_key in session_keys)
        self.event_controller.delete_event(event)

    def test_bad_create(self):
        event = self.dummy_event(-10005) #an event in the past
        with self.assertRaises(WebExError):
            self.event_controller.create_event(event)

    def test_bad_delete(self):
        with self.assertRaises(WebExError):
            self.event_controller.delete_event(WebExEvent(session_key='garbage82uiu988h32983y34'))

    def test_good_delete(self):
        event = self.event_controller.create_event(self.dummy_event())
        self.assertTrue(event)
        self.assertEquals(event,self.event_controller.delete_event(event))

    def dummy_event(self, minute_distance = 15):
        utc_future = (datetime.utcnow()+timedelta(minutes = minute_distance)).replace(tzinfo=pytz.utc)
        eastern = pytz.timezone('America/New_York')
        starts_at = utc_future.astimezone(eastern)
        title = "Dummy UnitTest Event [%s]" % str(uuid.uuid4())[0:16]
        return WebExEvent(title, starts_at, 90, UNITTEST_EVENT_DESCRIPTION)
        

if __name__ == '__main__':
    unittest2.main()
