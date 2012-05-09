import unittest
from ..registrant import Registrant, GetGeneralRegistrants, GetAttendedRegistrants
from ..event import Event
from .helper import TestHelper
from ..exchange import BatchListExchange
from ..xutils import lazy_property
from sanetime import time

class RegistrantTest(unittest.TestCase):

    def setUp(self): 
        self.th = TestHelper()
        self.account = self.th.account

    def tearDown(self): pass

    def test_name_conversion(self):
        event = Event.random(self.account)
        r = Registrant(event, first_name = 'John', last_name='Smith', name='John Smith')
        self.assertEquals('John', r.first_name)
        self.assertEquals('Smith', r.last_name)
        self.assertEquals('John Smith', r.name)
        r = Registrant(event, first_name='', last_name='Jones', name='')
        self.assertIsNone(r.first_name)
        self.assertEquals('Jones', r.last_name)
        self.assertEquals('Jones', r.name)

    def test_equality(self):
        event = Event.random(self.account)
        registrant1 = Registrant.random(event)

        self.assertEquals(registrant1, registrant1)
        self.assertTrue(registrant1 == registrant1)
        self.assertFalse(registrant1 != registrant1)
        self.assertFalse(registrant1 < registrant1)
        self.assertFalse(registrant1 > registrant1)
        self.assertTrue(registrant1 >= registrant1)
        self.assertTrue(registrant1 <= registrant1)

        registrant2 = Registrant.random(event)
        registrant1.email = '00000000.00000000@0000000000000000.com'

        self.assertNotEquals(registrant1, registrant2)
        self.assertFalse(registrant1 == registrant2)
        self.assertTrue(registrant1 != registrant2)
        self.assertTrue(registrant1 < registrant2)
        self.assertFalse(registrant1 > registrant2)
        self.assertFalse(registrant1 >= registrant2)
        self.assertTrue(registrant1 <= registrant2)

    def test_clone(self):
        event = Event.random(self.account)
        registrant = Registrant.random(event)
        clone = registrant.clone()
        extra = Registrant.random(event)
        self.assertEquals(registrant, clone)
        self.assertNotEquals(registrant, extra)

    def test_view_collapsing(self):
        event = Event.random(self.account)
        r1 = Registrant(event, email="dude@hs.com",viewings=[[time(s=100),time(s=200)]])
        self.assertEquals([[time(s=100),time(s=200)]], r1.viewings)
        r2 = Registrant(event,email="dude@hs.com",viewings=[[time(s=300),time(s=400)]])
        self.assertEquals([[time(s=300),time(s=400)]], r2.viewings)
        r1.merge(r2)
        self.assertEquals([[time(s=100),time(s=200)],[time(s=300),time(s=400)]], r1.viewings)

    def test_viewings(self):
        event = Event.random(self.account)
        r = Registrant(event, email="dude@hs.com")
        self.assertIsNone(r.started_at)
        self.assertIsNone(r.stopped_at)
        self.assertIsNone(r.duration_in_minutes)
        r.merge(Registrant(event, email="dude@hs.com", viewings=[[time(s=60*10),time(s=60*30)]]))
        self.assertEquals(60*10, r.started_at.s)
        self.assertEquals(60*30, r.stopped_at.s)
        self.assertEquals(20, r.duration_in_minutes)
        r.merge(Registrant(event, email="dude@hs.com", viewings=[[time(s=60*50),time(s=60*55)]]))
        self.assertEquals(60*10, r.started_at.s)
        self.assertEquals(60*55, r.stopped_at.s)
        self.assertEquals(45, r.duration_in_minutes)

    def _get_or_create_event(self, size):
        title = 'unittests: permanent event (%s)' % size
        event = None
        for e in self.account.listed_events:
            if e.title == title: return e
        event = Event.random(self.account)
        event.title = title
        event.starts_at = time('2013-01-01 00:00:00', tz='America/New_York')
        event.create()
        event.create_registrants(Registrant.random(event, size))
        return event

    @lazy_property
    def big_event(self): return self._get_or_create_event(4000)
    @lazy_property
    def moderate_event(self): return self._get_or_create_event(500)

    @unittest.skip('huge bulk actions: may trigger 503s')
    def test_huge_crud(self):
        size = 3000
        event = Event.random(self.account).create()
        registrants = dict((r.email,r) for r in Registrant.random(event, size))
        start = time()
        expected = dict((r.email,r) for r in event.create_registrants(registrants.values()))
        after_create = time()
        actual = dict((r.email,r) for r in event.general_registrants)
        after_listing = time()
        self.assertEquals(registrants, expected)
        self.assertEquals(expected, actual)
        self.assertEquals(size, len(expected))
        print "\nCREATE TIMING: %sms\nLISTING TIMING: %sms" % ((after_create-start).ms, (after_listing-after_create).ms,)

    def test_general_registrants(self, event=None):
        ev = event or self.moderate_event
        registrants = ev.general_registrants
        self.assertEquals(len(registrants), len(set(r.email for r in registrants)))
        if ev == self.moderate_event:  # random events may have duplicate emails that were merged during batching
            count = GetGeneralRegistrants(ev, 1, 0).answer[1]
            self.assertEquals(count, len(registrants))

    def test_attended_registrants(self, event=None):
        ev = event or self.moderate_event
        #count = GetAttendedRegistrants(ev, 1, 0).answer[1]
        registrants = ev.attended_registrants
        self.assertEquals(len(registrants), len(set(r.email for r in registrants)))
        #TODO: any better way to verify?  maybe not

    def test_registrants(self, event=None):
        ev = event or self.moderate_event
        registrants = ev.registrants
        emails = set(r.email for r in registrants)
        general_emails = set(r.email for r in ev.general_registrants)
        attended_emails = set(e.email for e in ev.attended_registrants)
        self.assertEquals(emails, general_emails | attended_emails)
        if ev == self.moderate_event:  # random events may have duplicate emails that were merged during batching
            count = GetGeneralRegistrants(ev, 1, 0).answer[1]
            self.assertEquals(count, len(registrants))
        return registrants

    @unittest.skip('long running')
    def test_sync_general_registrants(self, event=None):
        ev = event or self.big_event
        registrants = ev.general_registrants
        sync_registrants = BatchListExchange(self.event, GetGeneralRegistrants, 'email', batch_size=2, overlap=1, async=False).items
        self.assertEquals(registrants, sync_registrants)

    @unittest.skip('long running')
    def test_sync_attended_registrants(self, event=None):
        ev = event or self.big_event
        registrants = ev.attended_registrants
        sync_registrants = BatchListExchange(self.event, GetAttendedRegistrants, 'email', batch_size=2, overlap=1, async=False).items
        self.assertEquals(registrants, sync_registrants)

    @unittest.skip('super thorough, super long test')
    def test_max_timing(self):  # against all known accounts, and all their events:
        from pprint import pprint
        max_info = (None, 0)
        for k in self.th._accounts_dict.keys():
            pprint(self.th[k])
            for e in self.th[k].events:
                started = time()
                registrants = e.registrants
                elapsed = (time()-started).s
                if elapsed > max_info[1]: 
                    max_info = ("%s %s %s %s" % (e.account.site_name, e.session_key, e.title, len(registrants)), elapsed)
                    print max_info
        print max_info

    @unittest.skip('super thorough, super long test')
    def test_blanket(self):  # against all known accounts, and all their events:
        from pprint import pprint
        for k in self.th._accounts_dict.keys():
            pprint(self.th[k])
            for e in self.th[k].events:
                pprint(e)
                self.test_general_registrants(e)
                self.test_attended_registrants(e)
                registrants = self.test_registrants(e)
                pprint(registrants)

    def test_crud(self):
        event = Event.random(self.account).create()
        registrants = dict((r.email,r) for r in event.get_general_registrants(True))
        
        new_registrant = Registrant.random(event).create()
        registrants_after_create = dict((r.email,r) for r in event.get_general_registrants(True))
        self.assertNotIn(new_registrant.email, registrants)
        self.assertIn(new_registrant.email, registrants_after_create)
        self.assertEquals(new_registrant, registrants_after_create[new_registrant.email])

        deleted_registrant = new_registrant.delete()
        registrants_after_delete = dict((r.email,r) for r in event.get_general_registrants(True))
        self.assertIn(deleted_registrant.email, registrants_after_create)
        self.assertNotIn(deleted_registrant.email, registrants_after_delete)

        #test same on a nameless registrant
        new_registrant = Registrant.random(event)
        new_registrant.first_name = None
        new_registrant.last_name = None
        new_registrant.create()

        registrants_after_create = dict((r.email,r) for r in event.get_general_registrants(True))
        self.assertNotIn(new_registrant.email, registrants)
        self.assertIn(new_registrant.email, registrants_after_create)
        self.assertEquals(new_registrant, registrants_after_create[new_registrant.email])
        
        deleted_registrant = new_registrant.delete()
        registrants_after_delete = dict((r.email,r) for r in event.get_general_registrants(True))
        self.assertIn(deleted_registrant.email, registrants_after_create)
        self.assertNotIn(deleted_registrant.email, registrants_after_delete)

        event.delete()


    def test_batch_crud(self):
        event = Event.random(self.account).create()
        registrants = dict((r.email,r) for r in event.get_general_registrants(True))

        new_registrants = Registrant.random(event, 10)
        new_registrants = dict((r.email,r) for r in event.create_registrants(new_registrants))
        registrants_after_create = dict((r.email,r) for r in event.get_general_registrants(True))
        self.assertEquals({}, dict((email, registrants[email]) for email in set(registrants) & set(new_registrants)))
        self.assertEquals(new_registrants, dict((email, registrants_after_create[email]) for email in (set(registrants_after_create) & set(new_registrants))))

        deleted_registrants = dict((r.email, r) for r in event.delete_registrants(new_registrants.values()))
        registrants_after_delete = dict((r.email,r) for r in event.get_general_registrants(True))
        self.assertEquals(deleted_registrants, dict((email, registrants_after_create[email]) for email in set(registrants_after_create) & set(deleted_registrants)))
        self.assertEquals({}, dict((email, registrants_after_delete[email]) for email in set(registrants_after_delete) & set(deleted_registrants)))
        event.delete()
        
