from .utils import grab, nstrip, mpop, nint, find_all
from sanetime import sanetztime
from . import timezone
from .exchange import GetListExchange


class Event(object):
    def __init__(self, account, **kwargs):
        super(Event,self).__init__()
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
        attrs = ['title','starts_at','ends_at','started_at','ended_at','description','session_key','visibility']
        for a in attrs:
            setattr(self, a, getattr(self, a, None) or getattr(event, a, None))

    @property
    def starts_at(self): return self._starts_at or self._started_at
    
    @property
    def ends_at(self): return self._ends_at or self._ended_at

    @property
    def started_at(self): return self._started_at or self._starts_at

    @property
    def ended_at(self): return self._ended_at or self._ends_at

    def __eq__(self, that):
        return self.__dict__ == that.__dict__


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

