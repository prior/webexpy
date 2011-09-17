from lxml import etree
import datetime
import dateutil.parser
import pytz
import pprint

from utils import ATTENDEE_NS,HISTORY_NS,COMMON_NS
from attendee import WebExAttendee


class WebExAttendeeController(object):
    def __init__(self, webex):
        self.webex = webex

    def create_attendee(self,attendee):
        xml = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.CreateMeetingAttendee">
  <person>
    <firstName>%s</firstName>
    <lastName>%s</lastName>
    <email>%s</email>
  </person>
  <sessionKey>%s</sessionKey>
</bodyContent>
"""
        xml %= (attendee.first_name, attendee.last_name, attendee.email, attendee.event.session_key)
        response = self.webex.query(xml)
        attendees = []
        if response.success:
            elem = response.body_content.find("{%s}attendeeId"%ATTENDEE_NS)
            if elem is not None:
                attendee.id = elem.text
                return True
        return False
    
    def delete_attendee(self, attendee):
        xml = """
<bodyContent xsi:type= "java:com.webex.service.binding.attendee.DelMeetingAttendee">
  <attendeeID>%s</attendeeID>
</bodyContent>
"""
        xml %= self.attendee.id
        response = self.webex.query(xml)
        if response.success:
            return attendee
        return False

    def list_enrolled_attendees(self, event):
        xml = """
<bodyContent xsi:type="java:com.webex.service.binding.attendee.LstMeetingAttendee">
  <meetingKey>%s</meetingKey>
</bodyContent>
"""
        xml %= event.session_key
        response = self.webex.query(xml)
        attendees = []
        if response.success:
            for elem in response.body_content.findall('{%s}attendee'%ATTENDEE_NS):
                email = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}email'%COMMON_NS).text
                first_name = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}firstName'%COMMON_NS).text
                last_name = elem.find('{%s}person'%ATTENDEE_NS).find('{%s}lastName'%COMMON_NS).text
                attendees.append(WebExAttendee(email=email, first_name=first_name, last_name=last_name))
            return attendees
        return False

    def list_attended_attendees(self, event):
        xml = """
<bodyContent xsi:type= "java:com.webex.service.binding.history.LsteventattendeeHistory">
  <sessionKey>%s</sessionKey>
</bodyContent>
"""
        xml %= event.session_key
        response = self.webex.query(xml)
        if response.success:
            attendees_hash = {}
            for elem in response.body_content.findall('{%s}eventAttendeeHistory'%HISTORY_NS):
                email = elem.find('{%s}attendeeEmail'%HISTORY_NS).text
                start_datetime = dateutil.parser.parse(elem.find('{%s}startTime'%HISTORY_NS).text)
                end_datetime = dateutil.parser.parse(elem.find('{%s}endTime'%HISTORY_NS).text)
                duration = int(elem.find('{%s}duration'%HISTORY_NS).text)
                ip_address = elem.find('{%s}ipAddress'%HISTORY_NS).text
                attendees_hash.setdefault(email,[]).append(WebExAttendee(email=email,start_datetime=start_datetime,end_datetime=end_datetime,duration=duration,ip_address=ip_address))
            # dedupes those attendees that popped on and off the webinar -- merges things down into a single WebExAttendee
            attendees = []
            for key,value in attendees_hash.items():
                attendee = value[0]
                for i in range(len(value)-1):
                    attendee.merge(value[i+1])
                attendees.append(attendee)
                
            return attendees
        return False

    def list_attendees(self, event):
        if event.start_datetime.astimezone(pytz.utc).replace(tzinfo=None) > datetime.datetime.utcnow():
            return self.list_enrolled_attendees(event)
        lst = self.list_enrolled_attendees(event) + self.list_attended_attendees(event)
        h = {}
        for attendee in lst:
            if h.get(attendee.email) is None:
                h[attendee.email] = attendee
            else:
                h[attendee.email] = h[attendee.email].merge(attendee)
          
        return h.values() 


 

