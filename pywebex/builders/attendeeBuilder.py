import webexBuilder as builder

class RegisterMeetingAttendee(builder.WebExBuilder)
    def __init__(self, plist):
        self.list=plist
        pass
    def makePeople(self)
        pass

    def getBodyXml(self):
        body= super(RegisterMeetingAttendee, self).getBodyXml(self)
        bodycontent=build.ET.SubElement(body, "bodyContent")
        bodycontent.set(build.XSI_URI+"type", "attendee:registerMeetingAttendee")
        attendee= builder.ET.SubElement(body, 'attendee')
        people= makePeople()
        for a in self.makePeople()
            attendee.append(a)
        return body

    
    

class CreateMeetingAttendee(builder.WebExBuilder)    
