import unittest2
import os
import datetime
import pytz
import uuid
import json
import pprint

from webex.utils import is_blank
from webex.webex import WebEx
from webex.event import WebExEvent
from webex.attendee import WebExAttendee
from webex.event_controller import WebExEventController
from webex.attendee_controller import WebExAttendeeController


# these integration tests are normally commented out so we don't incur their hits on every run of our test suite

class WebExFlexApiTest(unittest2.TestCase):
    def setUp(self):
        info = json.loads(open(os.path.join(os.path.dirname(__file__),'test_integration_account.json')).read())
        site_name = info['site_name'] if info.has_key('site_name') and not is_blank(info['site_name']) else None
        site_id = info['site_id'] if info.has_key('site_id') and not is_blank(info['site_id']) else None
        partner_id = info['partner_id'] if info.has_key('partner_id') and not is_blank(info['partner_id']) else None
        email = info['email'] if info.has_key('email') and not is_blank(info['email']) else None
        self.webex = WebEx(info['webex_id'], info['password'], site_name=site_name, site_id=site_id, partner_id=partner_id, email=email, debug=True)
        self.bad_site = WebEx('bad_webex_id', 'bad_password', site_name='bad_site_name', site_id='bad_site_id', email='bad_email@bad_email.com', debug=True)
        self.bad_creds = WebEx('bad_webex_id', 'bad_password', site_name=site_name, site_id=site_id, email=email, debug=True)

    @unittest2.skip('integration')
    def test_bad_request(self):
        event_list = WebExEventController(self.bad_creds).list_events()
      
    @unittest2.skip('integration')
    def test_list_events(self):
        event_list = WebExEventController(self.webex).list_events()
        for event in event_list:
            print event
        self.assertIsNotNone(event_list)
        self.assertTrue(len(event_list) > 0)

    @unittest2.skip('integration')
    def test_list_enrolled_attendees(self):
        event = WebExEvent(session_key=663640282)
        attendee_list = WebExAttendeeController(self.webex).list_enrolled_attendees(event)
        for attendee in attendee_list:
            print attendee
        self.assertIsNotNone(attendee_list)
        self.assertTrue(len(attendee_list) > 0)

    @unittest2.skip('integration')
    def test_list_attended_attendees(self):
        event = WebExEvent(session_key=663640282)
        attendee_list = WebExAttendeeController(self.webex).list_attended_attendees(event)
        for attendee in attendee_list:
            print attendee
        self.assertIsNotNone(attendee_list)
        self.assertTrue(len(attendee_list) > 0)

    @unittest2.skip('integration')
    def test_list_attendees(self):
        event = WebExEvent(session_key=663640282, start_datetime = pytz.utc.localize(datetime.datetime(2011,1,1)))
        attendee_list = WebExAttendeeController(self.webex).list_attendees(event)
        for attendee in attendee_list:
            print attendee
        self.assertIsNotNone(attendee_list)
        self.assertTrue(len(attendee_list) > 0)

    @unittest2.skip('integration')
    def test_create_attendee(self):
        event = WebExEvent(session_key=663640282)
        attendee = WebExAttendee('%s@test.com'%uuid.uuid4(), 'John', 'Smith', event)
        self.assertIsNone(attendee.id)
        self.assertTrue(WebExAttendeeController(self.webex).create_attendee(attendee))
        self.assertIsNotNone(attendee.id)
    
    @unittest2.skip('integration')
    def test_create_event(self):
        dt = datetime.datetime.utcnow()
        event_name = "Test %s%s%s%s%s [%s]" % (dt.year,dt.month,dt.day,dt.hour,dt.minute,uuid.uuid4())
        event_time = pytz.timezone('America/New_York').localize(datetime.datetime.now()+datetime.timedelta(minutes=5))
        event = WebExEvent(event_name, event_time, 45, "created by integration unittests")
        self.assertIsNone(event.session_key)
        self.assertTrue(WebExEventController(self.webex).create_event(event))
        self.assertIsNotNone(event.session_key)

if __name__ == '__main__':
    unittest2.main()
