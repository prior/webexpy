import unittest2
from nose.plugins.attrib import attr
import os

from webex.error import WebExError
from webex.event import Event
from webex.event_controller import EventController
from sanetime import sanetztime

import helper


class EventControllerTest(unittest2.TestCase):

    # these integration tests are normally commented out so we don't incur their hits on every run of our test suite
    def setUp(self):
        self.account = helper.get_account()
        self.event_controller = EventController(self.account)

    @attr('api')
    def test_list(self):
        new_events = [helper.generate_event(), helper.generate_event()]
        session_keys = [ev.session_key for ev in self.event_controller.list()]
        for ev in new_events:
            self.assertNotIn(ev.session_key, session_keys)
            self.event_controller.create(ev)
        session_keys = [ev.session_key for ev in self.event_controller.list()]
        for ev in new_events:
            self.assertIn(ev.session_key, session_keys)
            self.event_controller.delete(ev)

    @attr('api')
    def test_good_create(self):
        event = helper.generate_event()
        self.assertIsNone(event.session_key)
        self.assertEquals(event, self.event_controller.create(event))
        session_keys = [ev.session_key for ev in self.event_controller.list()]
        self.assertTrue(event.session_key)
        self.assertTrue(event.session_key in session_keys)
        self.event_controller.delete(event)

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
        event = [ev for ev in self.event_controller.list() if ev.session_key == event1.session_key][0]
        self.assertEquals(event.title, event1.title)
        self.assertNotEquals(event.title, event2.title)
        event.title = event2.title
        self.event_controller.update(event)
        event = [ev for ev in self.event_controller.list() if ev.session_key == event1.session_key][0]
        self.assertEquals(event.title, event2.title)
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
        event_list = self.event_controller.list()
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
