import logging_glue
import sys
from sanetime import sanetztime
import timezone
from event import Event
from utils import EVENT_NS
from base_controller import BaseController
from pprint import pformat

CREATE_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.event.CreateEvent">
  <accessControl>
    <listing>PUBLIC</listing>
    <sessionPassword>0000</sessionPassword>
  </accessControl>
  <schedule>
    <startDate>%s</startDate>
    <duration>%s</duration>
    <timeZoneID>%s</timeZoneID>
  </schedule>
  <metaData>
    <sessionName>%s</sessionName>
    <description>%s</description>
  </metaData>
</bodyContent>
"""

UPDATE_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.event.SetEvent">
  <accessControl>
    <listing>PUBLIC</listing>
    <sessionPassword>0000</sessionPassword>
  </accessControl>
  <event:sessionKey>%s</event:sessionKey>
  <schedule>
    <startDate>%s</startDate>
    <duration>%s</duration>
    <timeZoneID>%s</timeZoneID>
  </schedule>
  <metaData>
    <sessionName>%s</sessionName>
    <description>%s</description>
  </metaData>
</bodyContent>
"""

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
        xml = CREATE_XML % (
            event.starts_at.strftime("%m/%d/%Y %H:%M:%S"),
            event.duration,
            timezone.PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP[event.starts_at.tz.zone],
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
        xml = UPDATE_XML % (
            event.session_key,
            event.starts_at.strftime("%m/%d/%Y %H:%M:%S"),
            event.duration,
            timezone.PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP[event.starts_at.tz.zone],
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
        if response.success:
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
            self.debug("listed %s events (batch #%s)" % (len(events), options.get('batch_number','?')))
        return events

    def list_(self, **options):
        self.debug("listing events")
        items = self.assemble_batches(self._list_batch, **options)
        self.info("listed %s events" % len(items))
        return items

