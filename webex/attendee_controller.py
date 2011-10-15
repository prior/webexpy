from utils import ATTENDEE_NS,HISTORY_NS,COMMON_NS
from base_controller import BaseController
from attendee import Attendee
from sanetime.sanetime import SaneTime


CREATE_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.CreateMeetingAttendee">
  <person>
    <firstName>%s</firstName>
    <lastName>%s</lastName>
    <email>%s</email>
  </person>
  <sessionKey>%s</sessionKey>
</bodyContent>
"""

DELETE_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.DelMeetingAttendee">
  <attendeeID>%s</attendeeID>
</bodyContent>
"""

LIST_REGISTRANTS_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.attendee.LstMeetingAttendee">
  <meetingKey>%s</meetingKey>
</bodyContent>
"""

LIST_ATTENDEES_XML = """
<bodyContent xsi:type= "java:com.webex.service.binding.history.LsteventattendeeHistory">
  <sessionKey>%s</sessionKey>
</bodyContent>
"""

class AttendeeController(BaseController):
    def __init__(self, account, event, debug=False):
        super(AttendeeController, self).__init__(account, debug=debug)
        self.event = event

    def create(self, attendee):
        xml = CREATE_XML % (attendee.first_name, attendee.last_name, attendee.email, self.event.session_key)
        response = self.query(xml)
        if response.success:
            elem = response.body_content.find("{%s}attendeeId"%ATTENDEE_NS)
            if elem is not None:
                attendee.id = elem.text
                return attendee
        return False
    
    def delete(self, attendee=None, attendee_id=None):
        if attendee_id and not attendee:
            attendee = Attendee(id=attendee_id)
        xml = DELETE_XML % attendee.id
        response = self.query(xml)
        if response.success:
            return attendee
        return False

    def list_registrants(self):
        xml = LIST_REGISTRANTS_XML % self.event.session_key
        response = self.query(xml, empty_list_ok=True)
        attendees = []
        if response.success:
            for elem in response.body_content.findall('{%s}attendee'%ATTENDEE_NS):
                email = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}email'%COMMON_NS).text
                first_name = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}firstName'%COMMON_NS).text
                last_name = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}lastName'%COMMON_NS).text
                id = elem.find('{%s}attendeeId'%ATTENDEE_NS).text.strip()
                attendees.append(Attendee(id=id, email=email, first_name=first_name, last_name=last_name))
        return attendees

    def list_attendants(self):
        xml = LIST_ATTENDEES_XML % self.event.session_key
        response = self.query(xml, empty_list_ok=True)
        attendees = []
        if response.success:
            attendees_hash = {}
            for elem in response.body_content.findall('{%s}eventAttendeeHistory'%HISTORY_NS):
                email = elem.find('{%s}attendeeEmail'%HISTORY_NS).text
                started_at = SaneTime(elem.find('{%s}startTime'%HISTORY_NS).text, tz=self.event.starts_at.tz)
                stopped_at = SaneTime(elem.find('{%s}endTime'%HISTORY_NS).text, tz=self.event.starts_at.tz)
                duration = int(elem.find('{%s}duration'%HISTORY_NS).text)
                ip_address = elem.find('{%s}ipAddress'%HISTORY_NS).text
                attendees_hash.setdefault(email,[]).append(Attendee(email=email,started_at=started_at,stopped_at=stopped_at,duration=duration,ip_address=ip_address))
            # dedupes those attendees that popped on and off the webinar -- merges things down into a single WebExAttendee
            for key,value in attendees_hash.items():
                attendee = value[0]
                for i in range(len(value)-1):
                    attendee.merge(value[i+1])
                attendees.append(attendee)
                
        return attendees

    def list(self):
        if self.event.starts_at > SaneTime():
            return self.list_registrants()
        lst = self.list_registrants() + self.list_attendants()
        h = {}
        for attendee in lst:
            if h.get(attendee.email) is None:
                h[attendee.email] = attendee
            else:
                h[attendee.email] = h[attendee.email].merge(attendee)
          
        return h.values() 


 

