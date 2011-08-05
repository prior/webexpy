import xml.etree.ElementTree as ET


class WebExException(Exception):

    def __init__(self, eid, rn, se):
        self.eid=eid
        self.rn=rn
        self.suberrors=se
    def __str__(self):
        return repr("Error while making request to WebEx. Error ID:{0}. Reason is:{1}".format(self.eid, self.rn))

class WebEx:
  
    def __init__(self, wbid, pw, sid, sname, em):
        self.webexId=wbid
        self.password=pw
        self.siteId=sname
        self.siteName=sname
        self.email=em
        self.header= None
        self.setHeader()

    def setHeader(self):
        head=ET.Element("header")
        securitycontext= ET.SubElement(head, "securityContext")
        webid= ET.SubElement(securitycontext, "webExID")
        webid.text= self.webexId
        webpass=ET.SubElement(securitycontext, "password")
        webpass.text= self.password
        siteid=ET.SubElement(securitycontext, "siteID")
        siteid.text= self.siteId
        sitename= ET.SubElement(securitycontext, "siteName")
        sitename.text= self.siteName
        self.header= head
  
    def getHeader(self):
        return self.header
    
    def createEvent(self):
        pass

    def makeSchedule(self):
        pass

    def setEvent(self):
        pass

    def createSchedule(self):
        pass

    def parseResponse(self);
        pass

    
