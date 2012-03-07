import unittest2
import requests.async
from ..event import GetListedEvents,GetHistoricalEvents,Event,CreateEvent
from .helper import TestHelper
from ..exchange import BatchListExchange

th = TestHelper()

class EventTest(unittest2.TestCase):

    def setUp(self): 
        self.account = th.account

    def tearDown(self): pass

    def test_create_event(self):
        current_session_keys = [e.session_key for e in self.account.listed_events]; del self.account._listed_batch_list
        expected_events = [Event.random(self.account) for i in xrange(10)]
        cloned_events = [e.clone() for e in expected_events]
        exchanges = [CreateEvent(th.account, e) for e in cloned_events]
        for e,r,x in zip(exchanges, requests.async.map([e.request for e in exchanges]), expected_events):
            x.session_key = e.process_response(r).session_key
        self.assertEquals(expected_events, [e.answer for e in exchanges])
        expected_hash = dict((e.session_key,e) for e in expected_events)
        actual_hash = dict((e.session_key,e) for e in self.account.listed_events)
        for sk in current_session_keys:
            del actual_hash[sk]
        self.assertEquals(expected_hash, actual_hash)

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
        from pprint import pprint; pprint(events)

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



