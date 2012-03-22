import uuid
from .utils import grab, nstrip, mpop, nint, find_all, nfind_str, lazy_property
from sanetime import sanetztime,sanetime
from . import timezone
from .exchange import Exchange, GetListExchange, BatchListExchange, ParallelBatchListExchange
from .registrant import GetGeneralRegistrants, GetAttendedRegistrants
from . import exchange
from . import registrant
from xml.sax.saxutils import escape as xml_escape


class Event(object):
    def __init__(self, account, **kwargs):
        super(Event,self).__init__()
        self.account = account
        
        self.title = nstrip(mpop(kwargs, 'title', 'sessionName','confName'))

        self._starts_at = kwargs.pop('starts_at',None)
        self._ends_at = kwargs.pop('ends_at',None)
        self._started_at = kwargs.pop('started_at',None)
        self._ended_at = kwargs.pop('ended_at',None)

        if kwargs.get('timeZoneID'):
            tz = timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[int(kwargs['timeZoneID'])]
            if self._starts_at is None and kwargs.get('startDate'): self._starts_at = sanetztime(kwargs['startDate'], tz=tz)
            if self._ends_at is None and kwargs.get('endDate'): self._ends_at = sanetztime(kwargs['endDate'], tz=tz)

        if kwargs.get('timezone'):
            tz = timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[int(kwargs['timezone'])]
            if self._started_at is None and kwargs.get('sessionStartTime'): self._started_at = sanetztime(kwargs['sessionStartTime']).set_tz(tz)
            if self._ended_at is None and kwargs.get('sessionEndTime'): self._ended_at = sanetztime(kwargs['sessionEndTime']).set_tz(tz)

        self.duration = mpop(kwargs, 'duration') or None
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

    @lazy_property
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

    @lazy_property
    def _general_batch_list(self):
        return BatchListExchange(GetGeneralRegistrants, self, 'email', batch_size=200, overlap=3)

    @lazy_property
    def _attended_batch_list(self):
        return BatchListExchange(GetAttendedRegistrants, self, 'email', batch_size=50, overlap=2)

    def create_registrants(self, registrants):
        return exchange.batch_bulk_action(registrant.CreateRegistrants, registrants, batch_size=50)

    def delete_registrants(self, registrants):
        return exchange.batch_action(registrant.DeleteRegistrant, registrants)



    @property
    def starts_at(self): return self._starts_at or self._started_at
    @starts_at.setter
    def starts_at(self, starts_at): self._starts_at = starts_at
    
    @property
    def ends_at(self): return self._ends_at or self._ended_at
    @ends_at.setter
    def ends_at(self, ends_at): self._ends_at = ends_at

    @property
    def started_at(self): return self._started_at or self._starts_at
    @started_at.setter
    def started_at(self, started_at): self._started_at = started_at

    @property
    def ended_at(self): return self._ended_at or self._ends_at
    @ended_at.setter
    def ended_at(self, ended_at): self._ended_at = ended_at

    @property
    def duration(self): return self.scheduled_duration or self.actual_duration
    @duration.setter
    def duration(self, value):
        pass # noop-- not needed -- but maybe worth doing a sanity check here? TODO
        #if not value: return
        #if self._starts_at and not self._ends_at:
            #self._ends_at = self._starts_at + value*60*10**6
        #elif self._started_at and not self._ended_at:
            #self._ended_at = self._started_at + value*60*10**6
    
    @property
    def scheduled_duration(self): return self.starts_at and self.ends_at and (self.ends_at-self.starts_at+30*10**6)/(60*10**6)

    @property
    def actual_duration(self): return self.started_at and self.ended_at and (self.ended_at-self.started_at+30*10**6)/(60*10**6)

    @property
    def timezone(self):
        return self.started_at and self.started_at.tz or self.stopped_at and self.stopped_at.tz or self.starts_at and self.starts_at.tz or self.stops_at and self.stops_at.tz 

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
        (self.ends_at-self.starts_at+30*10**6)/(60*10**6),
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
            now = sanetztime(s=sanetime().s, tz='America/New_York')
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
