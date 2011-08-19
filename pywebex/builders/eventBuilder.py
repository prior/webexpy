import webexBuilder as build

class CreateEvent(build.WebExRequestBuilder):

    def __init__(self, head, rdict):
        self.header=head
        self.rdict=rdict

    def getBodyXml(self):
        body=super(CreateEvent,self).getBodyXml()
        bodycontent=build.ET.SubElement(body,"bodyContent")
        bodycontent.set(build.XSI_URI+"type", "event:createEvent")
        elementlist= self.createElementList()
        for e in elementlist:
            bodycontent.append(e)
        return body       

    def createSchedule(self):
        schedule= build.ET.Element("schedule")
        start= build.ET.SubElement(schedule, "startDate")
        start.text=self.rdict["startDate"]
        duration= build.ET.SubElement(schedule, "duration")
        duration.text=self.rdict["duration"]
        timezone= build.ET.SubElement(schedule, "timeZoneID")
        if self.rdict["timeZoneID"] == None:
           timezone.text='11'
        else:
           timezone.text=self.rdict['timeZoneID']
        return schedule

    def createElementList(self):
        elist=[]
        elist.append(self.createSchedule())
        elist.append(self.createMetaData()) 
        return elist

    def createMetaData(self):
        meta= build.ET.Element("metaData")
        name=build.ET.SubElement(meta,"sessionName")
        name.text= self.rdict["sessionName"]
        description= build.ET.SubElement(meta, "description")
        description.text=self.rdict["description"]
        return meta

class GetEvent(build.WebExRequestBuilder):

    def __init__(self, head, rdict):
        self.header= head
        self.rdict=rdict

    def getBodyXml(self):
        body=super(GetEvent,self).getBodyXml()
        bodycontent=build.ET.SubElement(body,"bodyContent")
        bodycontent.set(build.XSI_URI+"type", "event:getEvent")
        sessionkey= build.ET.SubElement(bodycontent, "sessionKey")
        sessionkey.text=self.rdict['key']
        return body

class setEvent(build.WebExRequestBuilder):

    def __init__(self, rdict):
        pass

    def getBodyXml(self):
        pass

    def getMetaData(self):
        pass 
