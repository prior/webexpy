import unittest2
import os
import datetime
import pytz
import uuid
import json
import pprint

from webex.utils import is_blank
from webex.webex import WebEx, WebExError
from webex.event import WebExEvent
from webex.attendee import WebExAttendee
from webex.event_controller import WebExEventController
from webex.attendee_controller import WebExAttendeeController


# these integration tests are normally commented out so we don't incur their hits on every run of our test suite

def webex_from_creds(creds):
    return WebEx(
        creds.get('webex_id'), 
        creds.get('password'), 
        site_name = creds.get('site_name'),
        site_id = creds.get('site_id'), 
        email = creds.get('email'), 
        partner_id = creds.get('partner_id'), 
        debug = True)

class WebExFlexApiTest(unittest2.TestCase):
    def setUp(self):
        self.creds = { 'webex_id':None, 'password':None, 'site_name':None, 'site_id':None, 'email':None, 'partner_id':None }
        try:
            self.creds.update(json.loads(open(os.path.join(os.path.dirname(__file__),'test_account.json')).read()))
        except IOError,err:
            print err
            self.fail("Unable to open 'test_account.json' for integration tests.\n  These test rely on the existence of that file and on it having valid webex credentials.")
        except ValueError, err:
            print err
            self.fail("'test_account.json' doesn't appear to be valid json!\n  These test rely on the existence of that file and on it having valid webex credentials.")
        self.webex = webex_from_creds(self.creds)

    @unittest2.skip('integration')
    def test_bad_credentials(self):
        self.creds['webex_id'] = 'bad_webex_id'
        self.creds['password'] = 'bad_password'
        webex = webex_from_creds(self.creds)
        with self.assertRaises(WebExError):
            event_list = WebExEventController(webex).list_events()
      
    @unittest2.skip('integration')
    def test_list_events(self):
        event_list = WebExEventController(self.webex).list_events()
        for event in event_list:
            print event
        self.assertIsNotNone(event_list)
        self.assertTrue(len(event_list) > 0)

    @unittest2.skip('integration')
    def test_id_password_site_name(self):
        webex = webex_from_creds(dict((k,self.creds[k]) for k in ['webex_id','password','site_name']))
        event_list = WebExEventController(webex).list_events()
        self.assertIsNotNone(event_list)
        self.assertTrue(len(event_list) > 0)

    @unittest2.skip('integration')
    def test_invalid_site_name(self):
        creds = dict((k,self.creds[k]) for k in ['webex_id','password'])
        creds['site_name'] = 'bad_si@#$@%te_name'
        with self.assertRaises(WebExError):
            webex_from_creds(creds)

    @unittest2.skip('integration')
    def test_wrong_site_name(self):
        creds = dict((k,self.creds[k]) for k in ['webex_id','password'])
        creds['site_name'] = 'bad_site_name'
        webex = webex_from_creds(creds)
        with self.assertRaises(WebExError):
            event_list = WebExEventController(webex).list_events()

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
