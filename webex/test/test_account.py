import unittest2
from .. import error as e
from .. import account
from ..account import Account
from ..event import GetListedEvents,GetHistoricalEvents
from .helper import TestHelper
from ..exchange import BatchListExchange
#from gevent import monkey
#monkey.patch_all(httplib=True)

th = TestHelper()

class AccountTest(unittest2.TestCase):

    def setUp(self): 
        self.account = th.account

    def tearDown(self): pass

    def test_invalid_account(self):
        with self.assertRaises(e.InvalidAccount): Account()
        with self.assertRaises(e.InvalidAccount): Account(username='test', password='test', site_name='234@234')
        with self.assertRaises(e.InvalidAccount): Account(username='test', password='test')
        with self.assertRaises(e.InvalidAccount): Account(username='test', site_name='test')
        with self.assertRaises(e.InvalidAccount): Account(password='test', site_name='test')

        a = Account(username='test', password='test', site_name='jlskjwxklvcjlkwje')
        with self.assertRaises(e.TimeoutError): account.GetVersion(a, request_opts={'timeout':0.1})

    def test_listed_events(self):
        count = GetListedEvents(self.account, 1, 0).answer[1]
        events = self.account.listed_events
        self.assertEquals(count, len(events))

    def test_historical_events(self):
        count = GetHistoricalEvents(self.account, 1, 0).answer[1]
        events = self.account.historical_events
        self.assertEquals(count, len(events))

    def test_events(self):
        events = self.account.events
        keys = set(e.session_key for e in events)
        listed_keys = set(e.session_key for e in self.account.listed_events)
        historical_keys = set(e.session_key for e in self.account.historical_events)
        self.assertEquals(keys, listed_keys | historical_keys)

    def test_version_info(self):
        self.assertEquals(('WebEx XML API V5.9.0','SP1'), th.account.version_info)
        self.assertEquals(5.9, th.account.version)
        self.assertEquals(5, th.account.major_version)

    def test_meetings_require_password(self):
        self.assertTrue(th.account.meetings_require_password)

    @unittest2.skip('sanity checks we don\'t need to run every time')
    def test_sync_listed_events(self):
        events = th.account.listed_events
        sync_events = BatchListExchange(th.account, GetListedEvents, 'session_key', batch_size=2, overlap=1, async=False).items
        self.assertEquals(events, sync_events)

    @unittest2.skip('sanity checks we don\'t need to run every time')
    def test_sync_historical_events(self):
        events = th.account.historical_events
        sync_events = BatchListExchange(th.account, GetHistoricalEvents, 'session_key', batch_size=2, overlap=1, async=False).items
        self.assertEquals(events, sync_events)



