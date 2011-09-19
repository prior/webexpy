import unittest2
import uuid
from datetime import datetime
from datetime import timedelta
import pytz
import pprint

from webex.error import WebExError
from webex.event import Event
from webex.attendee import Attendee
from webex.event_controller import EventController
from webex.attendee_controller import AttendeeController

import helper


class AttendeeControllerTest(unittest2.TestCase):

# these integration tests are normally commented out so we don't incur their hits on every run of our test suite
    def setUp(self):
        self.account = helper.get_account()
        self.event_controller = EventController(self.account)
        self.attendee_controller = AttendeeController(self.account, debug=False)
        self.event = self.event_controller.create(helper.generate_event())

    def tearDown(self):
        self.event_controller.delete(self.event)

    def test_create(self):
        attendee = helper.generate_attendee(self.event)
        self.assertIsNone(attendee.id)
        self.assertTrue(self.attendee_controller.create(attendee))
        self.assertIsNotNone(attendee.id)

    def test_list_registrants(self):
        new_registrants = [helper.generate_attendee(self.event), helper.generate_attendee(self.event)]
        registrant_ids = [a.id for a in self.attendee_controller.list_registrants(self.event)]
        for a in new_registrants:
            self.assertNotIn(a.id, registrant_ids)
            self.attendee_controller.create(a)
        registrant_ids = [a.id for a in self.attendee_controller.list_registrants(self.event)]
        for a in new_registrants:
            self.assertIn(a.id, registrant_ids)
            self.attendee_controller.delete(a)

    # difficult to test, cuz no way to programatically make an attendant see a video-- have to test this manually
    def test_list_attendants(self):
        attendee_list = self.attendee_controller.list_attendants(self.event)
        self.assertIsNotNone(attendee_list)
        for attendee in attendee_list:
            print attendee

    def test_bad_delete(self):
        with self.assertRaises(WebExError):
            self.attendee_controller.delete(Attendee(id=2983492342))

    def test_good_delete(self):
        attendee = helper.generate_attendee(self.event)
        self.attendee_controller.create(attendee)
        self.assertTrue(attendee)
        self.assertEquals(attendee,self.attendee_controller.delete(attendee))

if __name__ == '__main__':
    unittest2.main()
