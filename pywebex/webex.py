import xml.etree.ElementTree as ET
import urllib2 as url
import parsers.WebExResponseParser as Parser
from builders import *

class WebExException(Exception):
    """Exception thrown when response body from WebEx is an exception"""

    def __init__(self, eid, rn, se, xml):
        self.eid=eid
        self.rn=rn
        self.suberrors= None #TODO:Embed additional suberrors into output
        self.xml=xml
    def __str__(self):
        return repr("Error while making request to WebEx. Error ID:{0}. Reason is:{1}. Request:{2}".format(self.eid, self.rn,self.xml))

class WebExResponse(object):
    """Class that holds all the information from a WebEx response"""

    def __init__(self, result): 
        self.result=result
        self.reason=None
        self.exceptionId=None
        self.suberrors=None
    def __str__(self):
        pass

class WebExHeader(object):
    """Holds the header information for a WebEx request"""

    def __init__(self, wbid, pw, sid, sname, em):
        self.webexId=wbid
        self.password=pw
        self.siteId=sid
        self.siteName=sname
        self.email=em
     
    def __str__(self):
        return repr("WebExID: %s , Password: %s, SiteID: %s, SiteName: %s, Email: %s" % (self.webexId, self.password, self.siteId, self.siteName, self.email))

class WebEx(object):
    """Primary class of module which allows you to make requests through the WebEx XML API"""
  
    def __init__(self, wbid, pw, sname, em):
        self.header=WebExHeader(wbid,pw,None,sname,em)
    def getHeader(self):
        return self.header
    
    def createEvent(self,rdict):
        """Create meeting event"""
        builder=eventBuilder.CreateEvent(self.header, rdict)
        xml= builder.getRequestXml()
        self.makeRequest(xml)
        return self.response        

    def getEvent(self, rdict):
        """Get meeting event information"""       
        builder=eventBuilder.GetEvent(self.header,rdict)
        xml=builder.getRequestXml()
        self.makeRequest(xml)
        return self.response

    def setEvent(self):
        """Set meeting event"""
        requestbody= WebExBody("event:setEvent")  
        builder=eventBuilder.GetEvent(self.header, rdict)
        xml=builder.getRequestXml()
        self.makeRequest(xml)
        return self.response

    def addAttendee(self):
        request=WebExBody("att:createMeetingAttedee")

    def registerAttendee(self):
        request=WebExBody("att:registerMeetingAttendee")

    def createSchedule(self):
        pass

    def parseResponse(self,res):
        parser=Parser.WebExResponseParser(res, None)
        tree= parser.getWebExResponse() 
        response=WebExResponse(tree.header.response.result)
        if(response.result =='FAILURE'):
            response.reason= tree.header.response.reason
            response.exceptionId= tree.header.response.exceptionID
        return response 

    def setEmailTemplate(self):
        pass

    def makeRequest(self, xml):
    	request= WebExWebRequest(self.header.siteName,xml)
        try:
            status= request.executeRequest()
            self.rawresponse=request.response
            self.response= self.parseResponse(request.response.read())
            if self.response.result == 'FAILURE':
                raise WebExException(self.response.exceptionId, self.response.reason, None,xml)
        except url.HTTPError as httperr:
            raise
        except url.URLError as urlerr:
            raise

class WebExWebRequest(object): 
    """ This class does the actual request to XML and gets back a response """

    def __init__(self, sname, xml):
        self.sitename= sname
        self.requestxml= xml
        self.response= None

    def getRequestURL(self):
        rurl = "https://{0}.webex.com/WBXService/XMLService".format(self.sitename)
        return rurl

    def executeRequest(self):
        try:
            request=url.Request(self.getRequestURL(), self.requestxml)
            response=url.urlopen(request)
            self.response=response
        except url.HTTPError, httperr:
            raise
        except url.URLError, urlerr:
            raise

