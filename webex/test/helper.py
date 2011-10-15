import os
import json
from uuid import uuid4

from sanetime.sanetime import SaneTime

from webex.error import WebExError
from webex.account import Account
from webex.event import Event
from webex.attendee import Attendee


def get_account():
    filename = 'test_credentials.json'
    try:
        raw_text = open(os.path.join(os.path.dirname(__file__), filename)).read()
    except IOError:
        raise WebExError, """Unable to open '%s' for integration tests.\n
  These tests rely on the existence of that file and on it having valid webex credentials.""" % filename
    try:
        creds = json.loads(raw_text)
    except ValueError:
        raise WebExError, """'%s' doesn't appar to be valid json!\n
  These tests rely on the existence of that file and on it having valid webex credentials.""" % filename
    return Account(**creds)


UNITTEST_EVENT_DESCRIPTION = """This is a fake/dummy webinar event created by the unittest system to verify the WebEx systems are operational.  These events are normally deleted immediately after creation, but in the case that you are reading this, then some code failed along the way.  It's likely a temporary outage on the WebEx side.  Please feel free to delete this event manually and let us know if these keep cropping up."""

def generate_event(minute_distance = 15):
    starts_at = SaneTime(tz='America/New_York')+minute_distance*60*1000**2
    title = "Dummy UnitTest Event [%s]" % str(uuid4())[0:16]
    return Event(title, starts_at, 90, UNITTEST_EVENT_DESCRIPTION)

def generate_attendee(event=None):
    random = str(uuid4())
    return Attendee(email='%s@%s.com'%(random[0:8],random[8:16]), first_name='John%s'%random[16:20], last_name='Smith%s'%random[20:24])
