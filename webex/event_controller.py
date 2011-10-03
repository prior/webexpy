import dateutil.parser

from event import Event
from timezone import Timezone
from utils import EVENT_NS
from base_controller import BaseController


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
  <listControl>
    <startFrom>1</startFrom>
    <maximumNum>1000</maximumNum>
  </listControl>
  <order>
    <orderBy>STARTTIME</orderBy>
    <orderAD>DESC</orderAD>
  </order>
</bodyContent>
"""

class EventController(BaseController):
    def __init__(self, account, debug=False):
        super(EventController, self).__init__(account, debug=debug)

    def create(self, event):
        xml = CREATE_XML % (
            event.start_datetime.strftime("%m/%d/%Y %H:%M:%S"),
            event.duration,
            Timezone.from_localized_datetime(event.start_datetime).id,
            event.session_name,
            event.description)
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
            event.start_datetime.strftime("%m/%d/%Y %H:%M:%S"),
            event.duration,
            Timezone.from_localized_datetime(event.start_datetime).id,
            event.session_name,
            event.description)
        response = self.query(xml)
        if response.success:
            return event
        return False

    def delete(self, event=None, event_id=None):
        if event_id and not event:
            event = Event(session_key=event_id)
        xml = DELETE_XML % event.session_key
        response = self.query(xml)
        if response.success:
            return event
        return False

    def list(self):
        response = self.query(LIST_XML)
        events = []
        if response.success:
            for elem in response.body_content.findall("{%s}event"%EVENT_NS):
                session_name = elem.find("{%s}sessionName"%EVENT_NS).text
                start_datetime = dateutil.parser.parse(elem.find("{%s}startDate"%EVENT_NS).text)
                timezone_id = int(elem.find("{%s}timeZoneID"%EVENT_NS).text)
                duration = int(elem.find("{%s}duration"%EVENT_NS).text)
                description = elem.find("{%s}description"%EVENT_NS).text
                session_key = elem.find("{%s}sessionKey"%EVENT_NS).text
                event = Event(session_name, Timezone(timezone_id).localize_naive_datetime(start_datetime), duration, description, session_key)
                events.append(event)
            return events
        return False



