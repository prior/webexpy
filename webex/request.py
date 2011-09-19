from lxml import etree
import urllib2
import datetime
import dateutil.parser
import pytz
import pprint


class Request(object):
    def __init__(self, account, body_content):
        self.account = account
        self.body_content = body_content
        self.url = 'https://%s.webex.com/WBXService/XMLService' % account.site_name
        self.msg = account.request_xml_template % body_content 
        self.raw_request = urllib2.Request(self.url, self.msg)


