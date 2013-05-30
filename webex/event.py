import uuid
from utils.property import cached_property
from utils.string import nstrip
from utils.dict import mpop 
from xutils import grab, find_all, nfind_str
from sanetime import time
from . import timezone
from .exchange import Exchange, GetListExchange, BatchListExchange, ParallelBatchListExchange
from .registrant import GetGeneralRegistrants, GetAttendedRegistrants
from . import exchange
from . import registrant
from . import mixins
from xml.sax.saxutils import escape as xml_escape


class Event(mixins.Event):
    def __init__(self, account, **kwargs):
        super(Event,self).__init__()
        self.account = account
        self.title = nstrip(mpop(kwargs, 'title', 'sessionName','confName'))
        self._starts_at = mpop(kwargs,'starts_at','_starts_at')
        self._ends_at = mpop(kwargs,'ends_at','_ends_at')
        self._started_at = mpop(kwargs,'started_at','_started_at')
        self._ended_at = mpop(kwargs,'ended_at','_ended_at')

        if kwargs.get('timeZoneID'): # this comes from normal listing
            tz = timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[int(kwargs['timeZoneID'])]
            if self._starts_at is None and kwargs.get('startDate'): self._starts_at = time(kwargs['startDate'], tz)
            if self._ends_at is None and kwargs.get('endDate'): self._ends_at = time(kwargs['endDate'], tz)

        if kwargs.get('timezone'): # this comes form historical listing
            tz = timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[int(kwargs['timezone'])]
            if self._started_at is None and kwargs.get('sessionStartTime'): self._started_at = time(kwargs['sessionStartTime']).set_tz(tz)
            if self._ended_at is None and kwargs.get('sessionEndTime'): self._ended_at = time(kwargs['sessionEndTime']).set_tz(tz)

        self.description = mpop(kwargs, 'description') or None
        self.session_key = mpop(kwargs, 'session_key', 'sessionKey')
        self.visibility = mpop(kwargs, 'listing', 'listStatus', fallback=account.meetings_must_be_unlisted and 'UNLISTED' or 'PUBLIC').strip().lower()

    def merge(self, event):
        attrs = ['title','_starts_at','_ends_at','_started_at','_ended_at','description','session_key','visibility']
        for a in attrs:
            setattr(self, a, getattr(self, a, None) or getattr(event, a, None))
        return self

    #TODO: deal with scenario where times are equal but timezones are different -- what should we do?
    def __cmp__(self, other):
        attrs = ['starts_at','ends_at','started_at','ended_at','session_key','title','description','visibility']
        for a in attrs:
            left = getattr(self,a,None)
            right = getattr(other,a,None)
            if left and right:
                result = cmp(left,right)
                if result != 0: return result
            elif right:
                return -1
            elif left:
                return 1
        return 0

    def clone(self):
        return Event(self.account).merge(self)

    def create(self): return CreateEvent(self).answer
    def update(self): return UpdateEvent(self).answer
    def delete(self): return DeleteEvent(self).answer

    @property
    def general_registrants(self): return self.get_general_registrants()

    @property
    def attended_registrants(self): return self.get_attended_registrants()

    @cached_property
    def registrants(self): return self.get_registrants()

    def get_general_registrants(self, bust=False):
        if bust: del self._general_batch_list
        return self._general_batch_list.items

    def get_attended_registrants(self, bust=False):
        if bust: del self._attended_batch_list
        return self._attended_batch_list.items

    def get_registrants(self, bust=False):
        if bust: 
            del self.registrants
            del self._general_batch_list
            del self._attended_batch_list
        return ParallelBatchListExchange([self._general_batch_list, self._attended_batch_list]).items

    @cached_property
    def _general_batch_list(self):
        return BatchListExchange(GetGeneralRegistrants, self, 'email', batch_size=200, overlap=3)

    @cached_property
    def _attended_batch_list(self):
        return BatchListExchange(GetAttendedRegistrants, self, 'email', batch_size=50, overlap=2)

    def create_registrants(self, registrants):
        return exchange.batch_bulk_action(registrant.CreateRegistrants, registrants, batch_size=50)

    def delete_registrants(self, registrants):
        return exchange.batch_action(registrant.DeleteRegistrant, registrants)




    @property
    def upsert_xml(self):
        return u"""
<accessControl><listing>%s</listing>%s</accessControl>%s
<schedule><startDate>%s</startDate><duration>%s</duration><timeZoneID>%s</timeZoneID></schedule>
<metaData><sessionName>%s</sessionName><description>%s</description></metaData> """ % (
        self.visibility.upper(),
        self.account.meetings_require_password and '<sessionPassword>0000</sessionPassword>' or '',
        self.session_key and ('<sessionKey>%s</sessionKey>'%self.session_key) or '',
        self.starts_at.strftime("%m/%d/%Y %H:%M:%S"),
        (self.ends_at-self.starts_at).m,
        timezone.get_id(self.starts_at.tz.zone),
        xml_escape(self.title),
        xml_escape(self.description))

    def __repr__(self): return str(self)
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        return u"%s%s %s %s %s %s %sm" % (self._starts_at and 'L' or ' ', self._started_at and 'H' or ' ', self.session_key, self.starts_at.strftime("%d.%m.%y %H:%M"), self.title, self.starts_at.tz.zone, self.duration)


    @classmethod
    def random(kls, account, count=None):
        events = []
        for i in xrange(count or 1):
            guid = ''.join(str(uuid.uuid4()).split('-'))
            now = time(s=time().s,tz='America/New_York')
            events.append( Event(
                    account, 
                    title = u'unittest #%s &<>\xfc\u2603 ' % guid[:16],
                    description = u'#%s:  An event created by unittests.  If you\'re seeing this, then something went wrong.  All events created by unittests are immediately cleaned up. &<>\xfc\u2603 ' % guid,
                    starts_at = now+15*60*10**6,
                    ends_at = now+30*60*10**6))
        return count is None and events[0] or events


class GetListedEvents(GetListExchange):
    ns = 'event'
    def _list_input(self): 
        return u'<bodyContent xsi:type="java:com.webex.service.binding.event.LstsummaryEvent">%s</bodyContent>'
    def _process_list_xml(self, body_content):
        return [Event(self.account, **grab(elem, 'sessionName','startDate','endDate','timeZoneID','description','sessionKey','listStatus', ns='event')) for elem in find_all(body_content, 'event:event')]


class GetHistoricalEvents(GetListExchange):
    ns = 'history'
    def _list_input(self): 
        return u'<bodyContent xsi:type="java:com.webex.service.binding.history.LsteventsessionHistory">%s</bodyContent>'
    def _process_list_xml(self, body_content):
        return [Event(self.account, **grab(elem, 'confName','sessionStartTime','sessionEndTime','timezone','sessionKey', ns='history')) for elem in find_all(body_content, 'history:eventSessionHistory')]


class EventExchange(Exchange):
    def __init__(self, event, request_opts=None, **opts):
        super(EventExchange, self).__init__(event.account, request_opts, **opts)
        self.event = event


class CreateEvent(EventExchange):
    def _input(self): 
        return u'<bodyContent xsi:type="java:com.webex.service.binding.event.CreateEvent">%s</bodyContent>' % self.event.upsert_xml
    def _process_xml(self, body_content):
        self.event.session_key = nfind_str(body_content, 'event:sessionKey')
        return self.event


class UpdateEvent(EventExchange):
    def _input(self): 
        return u'<bodyContent xsi:type="java:com.webex.service.binding.event.SetEvent">%s</bodyContent>' % self.event.upsert_xml
    def _process_xml(self, body_content):
        return self.event


class DeleteEvent(EventExchange):
    def _input(self): 
        return u'<bodyContent xsi:type="java:com.webex.service.binding.event.DelEvent"><sessionKey>%s</sessionKey></bodyContent>' % self.event.session_key
    def _process_xml(self, body_content):
        return self.event
