import unittest2
from nose.plugins.attrib import attr
import os

from webex.error import WebExError
from webex.event import Event
from webex.event_controller import EventController
from sanetime import sanetztime

import helper
import logger


class EventControllerTest(unittest2.TestCase):

    # these integration tests are normally commented out so we don't incur their hits on every run of our test suite
    def setUp(self):
        print "\r"
        self.account = helper.get_account()
        self.event_controller = EventController(self.account)

    @attr('api')
    def test_listing_and_counts(self):
        new_events = [helper.generate_event(), helper.generate_event()]
        session_keys = [ev.session_key for ev in self.event_controller.list_()]
        self.assertEquals(len(session_keys), self.event_controller.count)
        for ev in new_events:
            self.assertNotIn(ev.session_key, session_keys)
            self.event_controller.create(ev)
        session_keys = [ev.session_key for ev in self.event_controller.list_()]
        self.assertEquals(len(session_keys), self.event_controller.count)
        for ev in new_events:
            self.assertIn(ev.session_key, session_keys)
            self.event_controller.delete(ev)

    def test_listing_offsets(self):
        event_count = self.event_controller.count
        if event_count < 10:  # ensure we're working with at least 10 items
            for i in xrange(event_count, 10, 1):
                self.event_controller.create(helper.generate_event())
            event_count = self.event_controller.count
        self.assertTrue(event_count >= 10)
        self.assertEquals(10, len(self.event_controller.list_(offset=0, max_number=10)))
        self.assertEquals(3, len(self.event_controller.list_(offset=3, max_number=3)))
        self.assertEquals(1, len(self.event_controller.list_(offset=1, max_number=1)))

    #@attr('api')
    #def test_noop_list(self):
        #account = helper.get_account('care2')
        #event_controller = EventController(account)
        #event_controller.list_()
        #self.assertTrue(True)

    @attr('api')
    def test_good_create(self):
        event = helper.generate_event()
        self.assertIsNone(event.session_key)
        self.assertEquals(event, self.event_controller.create(event))
        session_keys = [ev.session_key for ev in self.event_controller.list_()]
        self.assertTrue(event.session_key)
        self.assertTrue(event.session_key in session_keys)
#        self.event_controller.delete(event)

    @attr('api')
    def test_listing_playground(self):
        current_titles = [(e.session_key,e.title,e.starts_at,e.duration) for e in self.event_controller.list_()]
        historical_titles = [(e.session_key,e.title,e.starts_at,e.duration) for e in self.event_controller.list_historical()]
        from pprint import pprint;
        pprint(current_titles)
        pprint(historical_titles)

    @attr('api')
    def test_bad_create(self):
        event = helper.generate_event(-10005) #an event in the past that should make the create fail
        with self.assertRaises(WebExError):
            self.event_controller.create(event)

    @attr('api')
    def test_update(self):
        event1 = helper.generate_event()
        event2 = helper.generate_event()
        self.event_controller.create(event1)
        event = [ev for ev in self.event_controller.list_() if ev.session_key == event1.session_key][0]
        self.assertEquals(event.title, event1.title)
        self.assertEquals(event.starts_at.us/10**6, event1.starts_at.us/10**6)
        self.assertEquals(event.duration, event1.duration)
        self.assertEquals(event.description, event1.description)
        self.assertNotEquals(event.title, event2.title)
        event.title = event2.title
        self.event_controller.update(event)
        event = [ev for ev in self.event_controller.list_() if ev.session_key == event1.session_key][0]
        self.assertEquals(event.title, event2.title)
        self.assertEquals(event.starts_at.us/10**6, event1.starts_at.us/10**6)
        self.assertEquals(event.duration, event1.duration)
        self.assertEquals(event.description, event1.description)
        self.assertNotEquals(event.title, event1.title)

    @attr('api')
    def test_bad_delete(self):
        with self.assertRaises(WebExError):
            self.event_controller.delete(event_id='garbage82uiu988h32983y34')

    @attr('api')
    def test_good_delete(self):
        event = self.event_controller.create(helper.generate_event())
        self.assertTrue(event)
        self.assertEquals(event,self.event_controller.delete(event))

    def test_list_response_parsing(self):
        self.event_controller.xml_override = open(os.path.join(os.path.dirname(__file__),'example_LstsummaryEventResponse.xml')).read()
        event_list = self.event_controller.list_()
        self.assertEqual(3, len(event_list))
        event = event_list[0]
        self.assertIsNotNone(event)
        self.assertEquals("ec 0000000000", event.title)
        self.assertEquals(sanetztime(2004,4,3,10,tz='Asia/Shanghai'), event.starts_at)
        self.assertEquals(60, event.duration)
        self.assertEquals('xbxbxcxcbbsbsd', event.description)
        self.assertEquals('23357393', event.session_key)

    def test_create_response_parsing(self):
        self.event_controller.xml_override = open(os.path.join(os.path.dirname(__file__),'example_CreateEventResponse.xml')).read()
        event = Event("ec 000000000", sanetztime(2004,4,3,10,tz='Asia/Shanghai'), 60, 'xbxbxbxbxxxbx')
        self.assertIsNone(event.session_key)
        self.event_controller.create(event)
        self.assertIsNotNone(event.session_key)
        

if __name__ == '__main__':
    unittest2.main()
