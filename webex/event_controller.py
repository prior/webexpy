import logging_glue
import sys
from sanetime import sanetztime
import timezone
from event import Event
from utils import EVENT_NS, SERVICE_NS, HISTORY_NS
from base_controller import BaseController
from pprint import pformat

EVENT_UPSERT_XML = """
  <accessControl>
    <listing>PUBLIC</listing>
    %(extra_access_control)
  </accessControl>
  <schedule>
    <startDate>%(start_date)s</startDate>
    <duration>%(duration)s</duration>
    <timeZoneID>%(time_zone_id)s</timeZoneID>
  </schedule>
  <metaData>
    <sessionName>%(session_name)s</sessionName>
    <description>%(description)s</description>
  </metaData>
"""
EVENT_CREATE_XML = '<bodyContent xsi:type="java:com.webex.service.binding.event.CreateEvent">%s</bodyContent>' % EVENT_UPSERT_XML
EVENT_UPDATE_XML = '<bodyContent xsi:type="java:com.webex.service.binding.event.SetEvent">%s</bodyContent>' % EVENT_UPSERT_XML

class Action
    def __init__

    def build_request
    def execute




DELETE_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.event.DelEvent">
  <sessionKey>%s</sessionKey>
</bodyContent>
"""

LIST_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.event.LstsummaryEvent">
  %s
</bodyContent>
"""

HISTORICAL_LIST_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.history.LsteventsessionHistory">
  %s
</bodyContent>
"""

class EventController(BaseController):
    def __init__(self, account):
        super(EventController, self).__init__(account)
        self.log = logging_glue.get_log('webex.event_controller')

    def _log(self, action, event=None, level='info'):
        title = event and event.title or '?'
        headline = '%s... (event=%s account=%s)' % (action, title, self.account.webex_id)
        getattr(self.log, level)(headline)
        if event is not None:
            self.log.debug('%s...   event=%s   account=%s' % (
                action,
                event and pformat(vars(event), width=sys.maxint) or '',
                pformat(vars(self.account), width=sys.maxint) 
            ))

    def create(self, event):
        password_xml = ''
        if self.password_required:
            password_xml = '<sessionPassword>0000</sessionPassword>'
        xml = CREATE_XML % (
            password_xml,
            event.starts_at.strftime("%m/%d/%Y %H:%M:%S"),
            event.duration,
            timezone.get_id(event.starts_at.tz.zone),
            event.title,
            event.description )
        self.info("creating event", event)
        response = self.query(xml)
        if response.success:
            elem = response.body_content.find("{%s}sessionKey"%EVENT_NS)
            if elem is not None:
                event.session_key = elem.text
            return event
        return False

    def update(self, event):
        password_xml = ''
        if self.password_required:
            password_xml = '<sessionPassword>0000</sessionPassword>'
        xml = UPDATE_XML % (
            password_xml,
            event.session_key,
            event.starts_at.strftime("%m/%d/%Y %H:%M:%S"),
            event.duration,
            timezone.get_id(event.starts_at.tz.zone),
            event.title,
            event.description )
        self.info("updating event", event)
        response = self.query(xml)
        if response.success:
            return event
        return False

    def delete(self, event=None, event_id=None):
        if event_id and not event:
            event = Event(session_key=event_id)
        xml = DELETE_XML % event.session_key
        self.info("deleting event", event)
        response = self.query(xml)
        if response.success:
            return event
        return False

    def _list_batch(self, **options):
        xml = LIST_XML % options.get('list_options_xml','')
        self.debug("listing events (batch #%s)" % options.get('batch_number','?'))
        response = self.query(xml, empty_list_ok=True)
        events = []
        total_count = 0
        batch_count = 0
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
        return (events, batch_count, total_count)

    def _list_historical_batch(self, **options):
        xml = HISTORICAL_LIST_XML % options.get('list_options_xml','')
        self.debug("listing historical events (batch #%s)" % options.get('batch_number','?'))
        response = self.query(xml, empty_list_ok=True)
        events = []
        total_count = 0
        batch_count = 0
        if response.success:
            for elem in response.body_content.findall('{%s}matchingRecords'%HISTORY_NS):
                total_count = int(elem.find('{%s}total'%SERVICE_NS).text)
            for elem in response.body_content.findall("{%s}eventSessionHistory"%HISTORY_NS):
                title = elem.find("{%s}confName"%HISTORY_NS).text
                starts_at = elem.find("{%s}sessionStartTime"%HISTORY_NS).text
                timezone_id = int(elem.find("{%s}timezone"%HISTORY_NS).text)
                duration = int(elem.find("{%s}duration"%HISTORY_NS).text)
                session_key = elem.find("{%s}sessionKey"%HISTORY_NS).text
                starts_at = sanetztime(starts_at).set_tz(timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[timezone_id])
                event = Event(title, starts_at, duration, None, session_key)
                events.append(event)
                batch_count +=1
            self.debug("listed %s events (batch #%s)" % (len(events), options.get('batch_number','?')))
        return (events, batch_count, total_count)

    def list_(self, **options):
        self.debug("listing events")
        items = self.assemble_batches(self._list_batch, **options)
        self.info("listed %s events" % len(items))
        return items

    def list_historical(self, **options):
        self.debug("listing historical events")
        items = self.assemble_batches(self._list_historical_batch, **options)
        self.info("listed %s historical events" % len(items))
        return items

    def _get_count(self):
        return self.determine_count(self._list_batch)
    count = property(_get_count)




