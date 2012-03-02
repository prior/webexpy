import re
import requests
from . import utils as u
from .utils import lazy_property
from . import error
from .base import Base
from lxml import etree
from sanetime import sanetztime
from . import timezone

SUMMARY_LIST_XML = '<bodyContent xsi:type="java:com.webex.service.binding.event.LstsummaryEvent">%s</bodyContent>'
HISTORICAL_LIST_XML = '<bodyContent xsi:type="java:com.webex.service.binding.history.LsteventsessionHistory">%s</bodyContent>'
LIST_OPTIONS_XML = """
  <listControl>
    <startFrom>%(offset)s</startFrom>
    <maximumNum>%(size)s</maximumNum>
  </listControl>
"""

class Event(object):
    def __init__(self, account, **kwargs):
        super(Event,self).__init__()
        self.title = u.nstrip(u.mpop(kwargs, 'title', 'sessionName'))
        webex_starts_at = u.mpop(kwargs, 'starts_at', 'startDate')
        webex_timezone_id = u.nint(u.mpop(kwargs, 'timeZoneID'))
        self.starts_at = sanetztime(webex_starts_at, tz=webex_timezone_id and timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[webex_timezone_id])
        self.duration = u.nint(u.mpop(kwargs, 'duration', 'length'))
        self.description = u.mpop(kwargs, 'description') or None
        self.session_key = u.mpop(kwargs, 'session_key', 'sessionKey')
        self.visibility = u.mpop(kwargs, 'listing', 'listStatus', fallback='PUBLIC').strip().lower()


    @classmethod
    def _query_summary_list(kls, account, **kwargs): # offset, size
        if not kwargs.get('size'):

            
        return _query_list(account, SUMMARY_LIST_XML, kls._summary_etree_to_event, 'event:event', **kwargs)

    @classmethod
    def _query_historical_list(kls, account, **kwargs): # offset, size
        return _query_list(account, HISTORICAL_LIST_XML, kls._historical_etree_to_event, 'event:event', **kwargs)

    @classmethod
    def _query_list(kls, account, list_xml, xml_to_obj_f, parent_tag, **kwargs):
        kwargs.setdefault('offset',0)
        kwargs.setdefault('size',100000)
        try:
            body_content = account.request_etree(list_xml % (LIST_OPTIONS_XML%kwargs))
        except ApiError, err:
            if err.exception_id != 15: raise
            return []
        return [xml_to_obj_f(elem) for elem in findall(body_content, parent_tag)]


    @classmethod
    def _query_list_historical(kls, account, offset=None, size=None):
        account.request_etree(
        pass

    @classmethod
    def _list_summary_etree_to_event(kls, elem)
        u.grab(elem, 'sessionName','startDate','timeZoneID','duration','description','sessionKey','listStatus', ns='event')

        
        u.traverse(elem.
        
        
        if response.success:
            for elem in response.body_content.findall('{%s}matchingRecords'%EVENT_NS):
                total_count = int(elem.find('{%s}total'%SERVICE_NS).text)
            for elem in response.body_content.findall("{%s}event"%EVENT_NS):
                title = elem.find("{%s}sessionName"%EVENT_NS).text
                starts_at = elem.find("{%s}startDate"%EVENT_NS).text
                timezone_id = int(elem.find("{%s}timeZoneID"%EVENT_NS).text)
                duration = int(elem.find("{%s}duration"%EVENT_NS).text)
                description = elem.find("{%s}description"%EVENT_NS).text
                session_key = elem.find("{%s}sessionKey"%EVENT_NS).text
                starts_at = sanetztime(starts_at, tz=timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[timezone_id])
                event = Event(title, starts_at, duration, description, session_key)
                events.append(event)
                batch_count +=1
            self.debug("listed %s events (batch #%s)" % (len(events), options.get('batch_number','?')))
        

    @classmethod
    def _list_historical_etree_to_event(kls)

