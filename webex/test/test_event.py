import unittest
from ..event import GetListedEvents,GetHistoricalEvents,Event
from .helper import TestHelper
from ..exchange import BatchListExchange

class EventTest(unittest.TestCase):

    def setUp(self): 
        self.th = TestHelper()
        self.account = self.th.account

    def tearDown(self): pass

    def test_equality(self):
        event1 = Event.random(self.account)

        self.assertEquals(event1, event1)
        self.assertTrue(event1 == event1)
        self.assertFalse(event1 != event1)
        self.assertFalse(event1 < event1)
        self.assertFalse(event1 > event1)
        self.assertTrue(event1 >= event1)
        self.assertTrue(event1 <= event1)

        event2 = Event.random(self.account)
        event2.starts_at = event1.starts_at + 60*10**6
        self.assertNotEquals(event1, event2)
        self.assertFalse(event1 == event2)
        self.assertTrue(event1 != event2)
        self.assertTrue(event1 < event2)
        self.assertFalse(event1 > event2)
        self.assertFalse(event1 >= event2)
        self.assertTrue(event1 <= event2)

    def test_clone(self):
        event = Event.random(self.account)
        clone = event.clone()
        extra = Event.random(self.account)
        self.assertEquals(event, clone)
        self.assertNotEquals(event,extra)

    def test_single_crud(self):
        events = dict((e.session_key,e) for e in self.account.get_listed_events(True))

        new_event = Event.random(self.account)
        self.assertFalse(new_event.session_key)
        new_event.create()
        self.assertTrue(new_event.session_key)
        events_after_create = dict((e.session_key,e) for e in self.account.get_listed_events(True))
        self.assertNotIn(new_event.session_key, events)
        self.assertIn(new_event.session_key, events_after_create)
        self.assertEquals(new_event, events_after_create[new_event.session_key])

        updated_event = Event.random(self.account).merge(new_event)
        self.assertNotEquals(new_event, updated_event)
        updated_event.update()
        events_after_update = dict((e.session_key,e) for e in self.account.get_listed_events(True))
        self.assertNotIn(updated_event.session_key, events)
        self.assertIn(updated_event.session_key, events_after_create)
        self.assertNotEquals(updated_event, events_after_create[updated_event.session_key])
        self.assertIn(updated_event.session_key, events_after_update)
        self.assertEquals(updated_event, events_after_update[updated_event.session_key])

        deleted_event = updated_event.delete()
        events_after_delete = dict((e.session_key,e) for e in self.account.get_listed_events(True))
        self.assertIn(deleted_event.session_key, events_after_update)
        self.assertNotIn(deleted_event.session_key, events_after_delete)

    def test_batch_crud(self):
        events = dict((e.session_key,e) for e in self.account.get_listed_events(True))
        new_events = Event.random(self.account, 10)
        new_events = dict((e.session_key,e) for e in self.account.create_events(new_events))
        events_after_create = dict((e.session_key,e) for e in self.account.get_listed_events(True))
        self.assertEquals({}, dict((sk, events[sk]) for sk in set(events) & set(new_events)))
        self.assertEquals(new_events, dict((sk, events_after_create[sk]) for sk in (set(events_after_create) & set(new_events))))

        updated_events = dict((e.session_key, Event.random(self.account).merge(e)) for e in new_events.values())
        self.assertNotEquals(new_events, updated_events)
        updated_events = dict((e.session_key,e) for e in self.account.update_events(updated_events.values()))
        events_after_update = dict((e.session_key,e) for e in self.account.get_listed_events(True))
        self.assertEquals({}, dict((sk, events[sk]) for sk in set(events) & set(updated_events)))
        self.assertNotEquals(updated_events, dict((sk, events_after_create[sk]) for sk in set(events_after_create) & set(updated_events)))
        self.assertEquals(updated_events, dict((sk, events_after_update[sk]) for sk in set(events_after_update) & set(updated_events)))

        deleted_events = dict((e.session_key, e) for e in self.account.delete_events(updated_events.values()))
        events_after_delete = dict((e.session_key,e) for e in self.account.get_listed_events(True))
        self.assertEquals(deleted_events, dict((sk, events_after_update[sk]) for sk in set(events_after_update) & set(deleted_events)))
        self.assertEquals({}, dict((sk, events_after_delete[sk]) for sk in set(events_after_delete) & set(deleted_events)))
        
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
#        from pprint import pprint; pprint(events)

    @unittest.skip('sanity checks we don\'t need to run every time')
    def test_sync_listed_events(self):
        events = self.account.listed_events
        sync_events = BatchListExchange(self.account, GetListedEvents, 'session_key', batch_size=2, overlap=1, async=False).items
        self.assertEquals(events, sync_events)

    @unittest.skip('sanity checks we don\'t need to run every time')
    def test_sync_historical_events(self):
        events = self.account.historical_events
        sync_events = BatchListExchange(self.account, GetHistoricalEvents, 'session_key', batch_size=2, overlap=1, async=False).items
        self.assertEquals(events, sync_events)

