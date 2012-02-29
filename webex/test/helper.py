import sys
import os
import json
from .error import TestError
from ..utils import lazy_property
from ..account import Account


TEST_ACCOUNTS_FILENAME = 'test_accounts.json'
COMMON_DISCLAIMER = """
Unittests rely on the existence of the file: '%s', and on it having valid credentials at least for the 'default' key.  See %s.example for what this file should look like.  
Unittests are designed to be non-destructive to current data on the account.  
Of course a bug could break that design, but precluding that, you should be able to run these unittests on your webex account without it affecting the current state of things.
""" % (TEST_ACCOUNTS_FILENAME, TEST_ACCOUNTS_FILENAME)


class TestHelper(object):
    def __init__(self, **kwargs):
        super(TestHelper, self).__init__()

    @lazy_property
    def account(self):
        return self.get_account('default')

    def get_account(self, key):
        try:
            return Account(**self._accounts_dict[key])
        except KeyError:
            err = TestError("%s doesn't appear to have a 'default' key.  Unittest rely on the creds specified under that key.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER))
            raise err, None, sys.exc_info()[2]
            return 

    @lazy_property
    def _accounts_dict(self):
        try:
            raw_text = open(os.path.join(os.path.dirname(__file__), TEST_ACCOUNTS_FILENAME)).read()
        except IOError:
            err = TestError("Unable to open '%s' for integration tests.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER))
            raise err, None, sys.exc_info()[2]
        try:
            d = json.loads(raw_text)
        except ValueError:
            err = TestError("'%s' doesn't appear to be valid json!\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER))
            raise err, None, sys.exc_info()[2]
        return d


#from uuid import uuid4

#from sanetime import sanetztime

#from webex.event import Event
#from webex.attendee import Attendee

#UNITTEST_EVENT_DESCRIPTION = """This is a fake/dummy webinar event created by the unittest system to verify the WebEx systems are operational.  These events are normally deleted immediately after creation, but in the case that you are reading this, then some code failed along the way.  It's likely a temporary outage on the WebEx side.  Please feel free to delete this event manually and let us know if these keep cropping up."""

#def generate_event(minute_distance = 30):
    #starts_at = sanetztime(tz='America/New_York')+minute_distance*60*1000**2
    #title = "Dummy UnitTest Event [%s]" % str(uuid4())[0:16]
    #return Event(title, starts_at, 90, UNITTEST_EVENT_DESCRIPTION)

#def generate_attendee(event=None):
    #random = str(uuid4())
    #return Attendee(email='%s@%s.com'%(random[0:8],random[8:16]), first_name='John%s'%random[16:20], last_name='Smith%s'%random[20:24])
