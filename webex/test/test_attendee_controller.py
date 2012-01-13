import unittest2
from nose.plugins.attrib import attr

from webex.error import WebExError
from webex.event_controller import EventController
from webex.attendee_controller import AttendeeController
from sanetime import sanetime

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
    def test_bulk_create_registrants(self):
        size = 300
        attendees = []
        for i in xrange(size):
            attendee = helper.generate_attendee()
            attendees.append(attendee)
            self.assertIsNone(attendee.id)
        starts_at = sanetime()
        self.assertTrue(self.attendee_controller.bulk_create_registrants(attendees))
        print "compeleted in %.2f s" % ((sanetime().ms - starts_at.ms)/1000.0,)
        for i in xrange(size):
            self.assertIsNotNone(attendees[i].id)

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
    def test_volume_batching(self):   # looks like larger number is better here -- going with 500 for default
        # setup
        expected_attendee_ids = set()
        attendees = []
        for i in xrange(400):
            attendees.append(helper.generate_attendee())
        self.assertTrue(self.attendee_controller.bulk_create_registrants(attendees))
        for i in xrange(400):
            self.assertTrue(attendees[i].id)
        expected_attendee_ids = set(a.id for a in attendees)

        starts_at = sanetime()
        registrants = self.attendee_controller.list_registrants(batch_size=25)
        print "compeleted in %.2f s" % ((sanetime().ms - starts_at.ms)/1000.0,)
        
        actual_attendee_ids = set(a.id for a in registrants)
        self.assertEquals(400, len(actual_attendee_ids))
        self.assertEquals(expected_attendee_ids, actual_attendee_ids)

        starts_at = sanetime()
        registrants = self.attendee_controller.list_registrants(batch_size=50)
        print "compeleted in %.2f s" % ((sanetime().ms - starts_at.ms)/1000.0,)

        actual_attendee_ids = set(a.id for a in registrants)
        self.assertEquals(400, len(actual_attendee_ids))
        self.assertEquals(expected_attendee_ids, actual_attendee_ids)

        starts_at = sanetime()
        registrants = self.attendee_controller.list_registrants(batch_size=100)
        print "compeleted in %.2f s" % ((sanetime().ms - starts_at.ms)/1000.0,)

        actual_attendee_ids = set(a.id for a in registrants)
        self.assertEquals(400, len(actual_attendee_ids))
        self.assertEquals(expected_attendee_ids, actual_attendee_ids)

        starts_at = sanetime()
        registrants = self.attendee_controller.list_registrants(batch_size=200)
        print "compeleted in %.2f s" % ((sanetime().ms - starts_at.ms)/1000.0,)

        actual_attendee_ids = set(a.id for a in registrants)
        self.assertEquals(400, len(actual_attendee_ids))
        self.assertEquals(expected_attendee_ids, actual_attendee_ids)

        starts_at = sanetime()
        registrants = self.attendee_controller.list_registrants(batch_size=400)
        print "compeleted in %.2f s" % ((sanetime().ms - starts_at.ms)/1000.0,)

        actual_attendee_ids = set(a.id for a in registrants)
        self.assertEquals(400, len(actual_attendee_ids))
        self.assertEquals(expected_attendee_ids, actual_attendee_ids)


    @unittest2.skip('this test takes a while')
    @attr('api')
    def test_list_registrants_over_boundary_on_change(self):
        # setup
        TIMES = 10
        expected_attendee_ids = set()
        attendees = []
        for i in xrange(2*TIMES):
            attendees.append(helper.generate_attendee())
        self.assertTrue(self.attendee_controller.bulk_create_registrants(attendees))
        expected_attendee_ids = [a.id for a in attendees]
        self.assertTrue(all(expected_attendee_ids))
        self.assertEquals(len(expected_attendee_ids), len(set(expected_attendee_ids)))

        def list_pre_batch_callback(batch_number):
            if batch_number<=TIMES:
                attendees.append(helper.generate_attendee())
                self.assertTrue(self.attendee_controller.create_registrant(attendees[-1]))
                expected_attendee_ids.append(attendees[-1].id)
                self.assertTrue(attendees[-1].id)

        registrants = self.attendee_controller.list_registrants(batch_size=2, pre_callback=list_pre_batch_callback, batch_overlap=1)

        actual_attendee_ids = [a.id for a in registrants]
        self.assertTrue(all(actual_attendee_ids))
        self.assertEquals(len(actual_attendee_ids), len(set(actual_attendee_ids)))
        self.assertTrue(len(expected_attendee_ids) >= len(actual_attendee_ids))
        self.assertFalse(set(actual_attendee_ids)-set(expected_attendee_ids))


if __name__ == '__main__':
    unittest2.main()
