import uuid
from .utils import grab, nstrip, mpop, nint, find_all, nfind_str
from sanetime import sanetztime,sanetime
from . import timezone
from .exchange import GetListExchange, Exchange


class Event(object):
    def __init__(self, account, **kwargs):
        super(Event,self).__init__()
        self.account = account
        
        self.title = nstrip(mpop(kwargs, 'title', 'sessionName','confName'))

        starts_at = mpop(kwargs, 'starts_at', 'startDate')
        ends_at = mpop(kwargs, 'ends_at', 'endDate')
        scheduled_timezone_id = nint(mpop(kwargs, 'timeZoneID', 'timezone'))
        scheduled_timezone = scheduled_timezone_id and timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[scheduled_timezone_id]
        self._starts_at = starts_at and sanetztime(starts_at, tz=scheduled_timezone)
        self._ends_at = ends_at and sanetztime(ends_at, tz=scheduled_timezone)

        started_at = mpop(kwargs, 'started_at', 'sessionStartTime')
        ended_at = mpop(kwargs, 'ended_at', 'sessionEndTime')
        actual_timezone_id = nint(mpop(kwargs, 'timezone', 'timeZoneID')) or scheduled_timezone_id
        actual_timezone = actual_timezone_id and timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[actual_timezone_id]
        self._started_at = started_at and sanetztime(started_at, tz=actual_timezone)
        self._ended_at = ended_at and sanetztime(ended_at, tz=actual_timezone)

        self.description = mpop(kwargs, 'description') or None
        self.session_key = mpop(kwargs, 'session_key', 'sessionKey')
        self.visibility = mpop(kwargs, 'listing', 'listStatus', fallback='PUBLIC').strip().lower()

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

    def create(self): return CreateEvent(self.account, self).answer
    def update(self): return UpdateEvent(self.account, self).answer
    def delete(self): return DeleteEvent(self.account, self).answer


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
    
    @property
    def scheduled_duration(self): return self.starts_at and self.ends_at and (self.ends_at-self.starts_at+30*10**6)/(60*10**6)

    @property
    def actual_duration(self): return self.started_at and self.ended_at and (self.ended_at-self.started_at+30*10**6)/(60*10**6)

    @property
    def upsert_xml(self):
        return """
<accessControl><listing>%s</listing>%s</accessControl>%s
<schedule><startDate>%s</startDate><duration>%s</duration><timeZoneID>%s</timeZoneID></schedule>
<metaData><sessionName>%s</sessionName><description>%s</description></metaData> """ % (
        self.visibility.upper(),
        self.account.meetings_require_password and '<sessionPassword>0000</sessionPassword>' or '',
        self.session_key and ('<sessionKey>%s</sessionKey>'%self.session_key) or '',
        self.starts_at.strftime("%m/%d/%Y %H:%M:%S"),
        (self.ends_at-self.starts_at+30*10**6)/(60*10**6),
        timezone.get_id(self.starts_at.tz.zone),
        self.title,
        self.description)


    def __str__(self):
        return repr(self)
    def __repr__(self):
        return "%s%s %s %s %s %s %ss" % (self._starts_at and 'L' or ' ', self._started_at and 'H' or ' ', self.session_key, self.starts_at.strftime("%d.%m.%y %H:%M"), self.title, self.starts_at.tz.zone, self.duration)

    @classmethod
    def random(kls, account, count=None):
        events = []
        for i in xrange(count or 1):
            guid = str(uuid.uuid4())[:16]
            now = sanetztime(s=sanetime().s, tz='America/New_York')
            events.append( Event(
                    account, 
                    title = 'unittest #%s' % guid,
                    description = '#%s:  An event created by unittests.  If you\'re seeing this, then something went wrong.  All events created by unittests are immediately cleaned up.' % guid,
                    starts_at = now+15*60*10**6,
                    ends_at = now+30*60*10**6))
        return count is None and events[0] or events


class GetListedEvents(GetListExchange):
    ns = 'event'
    def _list_input(self): 
        return '<bodyContent xsi:type="java:com.webex.service.binding.event.LstsummaryEvent">%s</bodyContent>'
    def _list_answer(self, body_content): 
        return [Event(self.account, **grab(elem, 'sessionName','startDate','endDate','timeZoneID','description','sessionKey','listStatus', ns='event')) for elem in find_all(body_content, 'event:event')]


class GetHistoricalEvents(GetListExchange):
    ns = 'history'
    def _list_input(self): 
        return '<bodyContent xsi:type="java:com.webex.service.binding.history.LsteventsessionHistory">%s</bodyContent>'
    def _list_answer(self, body_content): 
        return [Event(self.account, **grab(elem, 'confName','sessionStartTime','sessionEndTime','timezone','sessionKey', ns='history')) for elem in find_all(body_content, 'history:eventSessionHistory')]


class EventExchange(Exchange):
    def __init__(self, account, event, request_opts=None, **opts):
        super(EventExchange, self).__init__(account, request_opts, **opts)
        self.event = event


class CreateEvent(EventExchange):
    def _input(self): 
        return '<bodyContent xsi:type="java:com.webex.service.binding.event.CreateEvent">%s</bodyContent>' % self.event.upsert_xml
    def _answer(self, body_content): 
        self.event.session_key = nfind_str(body_content, 'event:sessionKey')
        return self.event


class UpdateEvent(EventExchange):
    def _input(self): 
        return '<bodyContent xsi:type="java:com.webex.service.binding.event.SetEvent">%s</bodyContent>' % self.event.upsert_xml
    def _answer(self, body_content): 
        return self.event


class DeleteEvent(EventExchange):
    def _input(self): 
        return '<bodyContent xsi:type="java:com.webex.service.binding.event.DelEvent"><sessionKey>%s</sessionKey></bodyContent>' % self.event.session_key
    def _answer(self, body_content): 
        return self.event
