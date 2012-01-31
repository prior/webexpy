import sys
import logging_glue
from sanetime import sanetime
from pprint import pformat
from utils import ATTENDEE_NS,HISTORY_NS,COMMON_NS,SERVICE_NS
from base_controller import BaseController
from attendee import Attendee


CREATE_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.CreateMeetingAttendee">
  <person>
    <firstName>%s</firstName>
    <lastName>%s</lastName>
    <email>%s</email>
  </person>
  <sessionKey>%s</sessionKey>
  <joinStatus>INVITE</joinStatus>
</bodyContent>
"""

REGISTER_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.RegisterMeetingAttendee">
  <attendees>
    <person>
        <firstName>%s</firstName>
        <lastName>%s</lastName>
        <email>%s</email>
    </person>
    <sessionKey>%s</sessionKey>
    <joinStatus>ACCEPT</joinStatus>
  </attendees>
</bodyContent>
"""

INNER_REGISTER_XML = """
<attendees>
    <person>
        <firstName>%s</firstName>
        <lastName>%s</lastName>
        <email>%s</email>
    </person>
    <sessionKey>%s</sessionKey>
    <joinStatus>ACCEPT</joinStatus>
</attendees>
"""

OUTER_REGISTER_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.RegisterMeetingAttendee">
    %s
</bodyContent>
"""

DELETE_BY_ID_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.DelMeetingAttendee">
  <attendeeID>%s</attendeeID>
</bodyContent>
"""

DELETE_BY_EMAIL_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.DelMeetingAttendee">
  <attendeeEmail>
    <email>%s</email>
    <sessionKey>%s</sessionKey>
  </attendeeEmail>
</bodyContent>
"""

LIST_REGISTRANTS_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.attendee.LstMeetingAttendee">
  <meetingKey>%s</meetingKey>%s
</bodyContent>
"""

LIST_ATTENDEES_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.history.LsteventattendeeHistory">
  <sessionKey>%s</sessionKey>%s
</bodyContent>
"""

class AttendeeController(BaseController):
    def __init__(self, account, event):
        super(AttendeeController, self).__init__(account)
        self.event = event
        self.log = logging_glue.get_log('webex.attendee_controller')

    def _log(self, action, attendee=None, level='info'):
        email = attendee and attendee.email or '?'
        headline = '%s... (email=%s event=%s)' % (action, email, self.event.title)
        getattr(self.log, level)(headline)
        if attendee is not None:
            self.log.debug('%s...   attendee=%s   event=%s' % (
                action,
                attendee and pformat(vars(attendee), width=sys.maxint) or '',
                pformat(vars(self.event), width=sys.maxint) 
            ))

    def create_invitee(self, attendee):
        xml = CREATE_XML % (attendee.first_name, attendee.last_name, attendee.email, self.event.session_key)
        self.info("creating attendee", attendee)
        response = self.query(xml)
        if response.success:
            elem = response.body_content.find("{%s}attendeeId"%ATTENDEE_NS)
            if elem is not None:
                attendee.attendee_id = elem.text
                return attendee
        return False

    def create_registrant(self, attendee):
        xml = REGISTER_XML % (attendee.first_name, attendee.last_name, attendee.email, self.event.session_key)
        self.info("registering attendee", attendee)
        response = self.query(xml)
        if response.success:
            elem = response.body_content.find('{%s}register'%ATTENDEE_NS).find('{%s}attendeeID'%ATTENDEE_NS)
            if elem is not None:
                attendee.attendee_id = elem.text
                return attendee
        return False

    def bulk_create_registrants(self, attendees):
        batch_size = 50 
        batch_index = 0
        self.info("registering %s attendees in batches of %s" % (len(attendees), batch_size))
        while batch_index < len(attendees):
            xmls = []
            for attendee in attendees[batch_index:batch_index+batch_size]:
                xmls.append(INNER_REGISTER_XML % (attendee.first_name, attendee.last_name, attendee.email, self.event.session_key))
            xml = OUTER_REGISTER_XML % '\n'.join(xmls)
            response = self.query(xml)
            if response.success:
                i = 0
                for reg_elem in response.body_content.iter('{%s}register'%ATTENDEE_NS):
                    att_elem = reg_elem.find('{%s}attendeeID'%ATTENDEE_NS)
                    attendees[batch_index+i].attendee_id = att_elem.text
                    i += 1
            else:
                return attendees
            batch_index+=batch_size
        return attendees

    def delete(self, attendee=None, attendee_id=None):
        if attendee_id and not attendee:
            attendee = Attendee(attendee_id=attendee_id)
        if attendee.email and self.event.session_key:
            xml = DELETE_BY_EMAIL_XML % (attendee.email, self.event.session_key)
        elif attendee.attendee_id:
            xml = DELETE_BY_ID_XML % attendee.attendee_id
        self.info("deleting attendee", attendee)
        response = self.query(xml)
        if response.success:
            return attendee
        return False


    def _list_registrants_batch(self, **options):
        xml = LIST_REGISTRANTS_XML % (self.event.session_key, options.get('list_options_xml',''))
        self.debug("listing registrants (batch #%s)" % options.get('batch_number','?'))
        response = self.query(xml, empty_list_ok=True)
        attendees = []
        total = 0
        if response.success:
            for elem in response.body_content.findall('{%s}matchingRecords'%ATTENDEE_NS):
                total = int(elem.find('{%s}total'%SERVICE_NS).text)
            for elem in response.body_content.findall('{%s}attendee'%ATTENDEE_NS):
                email = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}email'%COMMON_NS).text
                name_elem = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}name'%COMMON_NS)
                first_name_elem = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}firstName'%COMMON_NS)
                last_name_elem = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}lastName'%COMMON_NS)
                first_name = name_elem is not None and name_elem.text.split(' ')[0] or first_name_elem is not None and first_name_elem.text or None
                last_name = name_elem is not None and ' '.join(name_elem.text.split(' ')[1:]) or last_name_elem is not None and last_name_elem.text or None
                attendee_id = elem.find('{%s}attendeeId'%ATTENDEE_NS).text.strip()
                attendees.append(Attendee(attendee_id=attendee_id, email=email, first_name=first_name, last_name=last_name))
            self.debug("listed %s registrants (batch #%s)" % (len(attendees), options.get('batch_number','?')))
        return (attendees, total)

    def list_registrants(self, **options):
        self.debug("listing registrants")
        options.setdefault('batch_size',500)
        options.setdefault('item_id','attendee_id')
        items = self.assemble_batches(self._list_registrants_batch, **options)
        self.info("listed %s registrants" % len(items))
        return items

    def _get_registrants_count(self):
        return self.determine_count(self._list_registrants_batch)
    registrants_count = property(_get_registrants_count)

    def _list_attendants_batch(self, **options):
        xml = LIST_ATTENDEES_XML % (self.event.session_key, options.get('list_options_xml',''))
        self.debug("listing attendants (batch #%s)" % options.get('batch_number','?'))
        response = self.query(xml, empty_list_ok=True)
        attendees = []
        total = 0
        if response.success:
            attendees_hash = {}
            for elem in response.body_content.findall('{%s}matchingRecords'%HISTORY_NS):
                total = int(elem.find('{%s}total'%SERVICE_NS).text)
            for elem in response.body_content.findall('{%s}eventAttendeeHistory'%HISTORY_NS):
                email = elem.find('{%s}attendeeEmail'%HISTORY_NS).text
                started_at = sanetime(elem.find('{%s}startTime'%HISTORY_NS).text) # looks to be UTC
                stopped_at = sanetime(elem.find('{%s}endTime'%HISTORY_NS).text) # looks to be UTC
                duration = int(elem.find('{%s}duration'%HISTORY_NS).text)
                ip_address = elem.find('{%s}ipAddress'%HISTORY_NS).text
                attendees_hash.setdefault(email,[]).append(Attendee(email=email,started_at=started_at,stopped_at=stopped_at,duration=duration,ip_address=ip_address))
            # dedupes those attendees that popped on and off the webinar -- merges things down into a single WebExAttendee
            for key,value in attendees_hash.items():
                attendee = value[0]
                for i in range(len(value)-1):
                    attendee.merge(value[i+1])
                attendees.append(attendee)
            self.debug("listed %s attendants (batch #%s)" % (len(attendees), options.get('batch_number','?')))
        return (attendees, total)

    def list_attendants(self, **options):
        self.debug("listing attendants")
        options.setdefault('batch_size',10)
        options.setdefault('item_id','email')
        items = self.assemble_batches(self._list_attendants_batch, **options)
        self.info("listed %s attendants" % len(items))
        return items

    def _get_attendants_count(self):
        return self.determine_count(self._list_attendants_batch)
    attendants_count = property(_get_attendants_count)


