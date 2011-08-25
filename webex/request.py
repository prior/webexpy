from lxml import etree
import urllib2
import datetime
import dateutil.parser
import pytz
import pprint


class WebExRequest(object):
    def __init__(self, webex, body_content):
        self.webex = webex
        self.body_content = body_content
        self.url = 'https://%s.webex.com/WBXService/XMLService' % webex.site_name
        self.msg = webex.request_xml % body_content 
        self.raw_request = urllib2.Request(self.url, self.msg)
        
