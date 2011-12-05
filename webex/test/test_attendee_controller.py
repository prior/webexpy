import unittest2
from nose.plugins.attrib import attr

from webex.error import WebExError
from webex.event_controller import EventController
from webex.attendee_controller import AttendeeController

import helper
import logger


class AttendeeControllerTest(unittest2.TestCase):

    # these integration tests are normally commented out so we don't incur their hits on every run of our test suite
    def setUp(self):
        print "\r"
        self.account = helper.get_account()
        self.event_controller = EventController(self.account)
        self.event = self.event_controller.create(helper.generate_event())
        self.attendee_controller = AttendeeController(self.account, self.event)

    def tearDown(self):
        self.event_controller.delete(self.event)

    @attr('api')
    def test_create_invitee(self):
        attendee = helper.generate_attendee()
        self.assertIsNone(attendee.id)
        self.assertTrue(self.attendee_controller.create_invitee(attendee))
        self.assertIsNotNone(attendee.id)

    @attr('api')
    def test_create_registrant(self):
        attendee = helper.generate_attendee()
        self.assertIsNone(attendee.id)
        self.assertTrue(self.attendee_controller.create_registrant(attendee))
        self.assertIsNotNone(attendee.id)

    @attr('api')
    def test_list_registrants(self):
        new_registrants = [helper.generate_attendee(), helper.generate_attendee()]
        registrant_ids = [a.id for a in self.attendee_controller.list_registrants()]
        for a in new_registrants:
            self.assertNotIn(a.id, registrant_ids)
            self.attendee_controller.create_registrant(a)
        registrant_ids = [a.id for a in self.attendee_controller.list_registrants()]
        for a in new_registrants:
            self.assertIn(a.id, registrant_ids)
            self.attendee_controller.delete(a)

    # difficult to test, cuz no way to programatically make an attendant see a video-- have to test this manually
    @attr('api')
    def test_list_attendants(self):
        attendee_list = self.attendee_controller.list_attendants()
        self.assertIsNotNone(attendee_list)
        for attendee in attendee_list:
            print attendee

    @attr('api')
    def test_bad_delete(self):
        with self.assertRaises(WebExError):
            self.attendee_controller.delete(attendee_id=2983492342)

    @attr('api')
    def test_good_delete_by_id(self):
        attendee = helper.generate_attendee()
        attendee = self.attendee_controller.create_invitee(attendee)
        self.assertTrue(attendee)
        self.assertIn(attendee.id, [a.id for a in self.attendee_controller.list_()])
        self.assertTrue(self.attendee_controller.delete(attendee))
        self.assertNotIn(attendee.id, [a.id for a in self.attendee_controller.list_()])

        attendee = helper.generate_attendee()
        attendee = self.attendee_controller.create_registrant(attendee)
        self.assertTrue(attendee)
        self.assertIn(attendee.id, [a.id for a in self.attendee_controller.list_()])
        self.assertTrue(self.attendee_controller.delete(attendee))
        self.assertNotIn(attendee.id, [a.id for a in self.attendee_controller.list_()])

    @attr('api')
    def test_good_delete_by_email(self):
        attendee = helper.generate_attendee()
        attendee = self.attendee_controller.create_invitee(attendee)
        self.assertTrue(attendee)
        attendee.id = None
        self.assertIn(attendee.email, [a.email for a in self.attendee_controller.list_()])
        self.assertTrue(self.attendee_controller.delete(attendee))
        self.assertNotIn(attendee.email, [a.email for a in self.attendee_controller.list_()])

        attendee = helper.generate_attendee()
        attendee = self.attendee_controller.create_registrant(attendee)
        self.assertTrue(attendee)
        attendee.id = None
        self.assertIn(attendee.email, [a.email for a in self.attendee_controller.list_()])
        self.assertTrue(self.attendee_controller.delete(attendee))
        self.assertNotIn(attendee.email, [a.email for a in self.attendee_controller.list_()])

    @attr('api')
    def test_batching_slicing_and_dicing(self):
        # setup
        expected_attendee_ids = set()
        for i in xrange(5):
            attendee = helper.generate_attendee()
            self.assertTrue(self.attendee_controller.create_registrant(attendee))
            expected_attendee_ids.add(attendee.id)

        for i in xrange(5):
            registrants = self.attendee_controller.list_registrants(batch_size=i+1)
            actual_attendee_ids = set(a.id for a in registrants)
            self.assertEquals(expected_attendee_ids, actual_attendee_ids)


    @unittest2.skip('this test takes a while')
    @attr('api')
    def test_volume_batching(self):
        # setup
        expected_attendee_ids = set()
        for i in xrange(101):
            attendee = helper.generate_attendee()
            self.assertTrue(self.attendee_controller.create_registrant(attendee))
            expected_attendee_ids.add(attendee.id)

        registrants = self.attendee_controller.list_registrants()
        actual_attendee_ids = set(a.id for a in registrants)
        self.assertEquals(expected_attendee_ids, actual_attendee_ids)



if __name__ == '__main__':
    unittest2.main()
