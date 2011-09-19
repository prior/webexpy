from lxml import etree
import urllib2
import datetime
import dateutil.parser
import pytz
import pprint
import re

from utils import is_blank
from request import Request
from response import Response
from utils import EP_NS

class BaseController(object):

    def __init__(self, account, debug=False):
        self.debug = debug
        self.account = account

    def get_api_version(self):
        xml_in = "\n<bodyContent xsi:type=\"java:com.webex.service.binding.ep.GetAPIVersion\"></bodyContent>"
        xml_out = self.query(xml_in).body_content
        version = xml_out.find("{%s}apiVersion"%EP_NS).text
        release = xml_out.find("{%s}release"%EP_NS).text
        return "%s : %s" % (version, release)

        
    def build_request_xml(self):
        if self.account.site_name and not re.compile(r'^[-a-zA-Z0-9_]*$').match(self.account.site_name):
            raise WebExError, "site_name is invalid!  It is expected to be an alphanumeric string."
        if is_blank(self.account.webex_id):
            raise WebExError, "Expected a webexId for API request validations, but did not receive one!"
        if is_blank(self.account.password):
            raise WebExError, "Expected a password for API request validations, but did not receive one!"
        if is_blank(self.account.site_id) and is_blank(self.account.site_name):
            raise WebExError, "Expected a siteId or a siteName for API request validations, but did not receive one!"
        securitySection = "\n<webExID>%s</webExID>" % self.account.webex_id
        securitySection += "\n<password>%s</password>" % self.account.password
        if is_blank(self.site_name):
            securitySection += "\n<siteId>%s</siteId>" % self.account.site_id
        else:
            securitySection += "\n<siteName>%s</siteName>" % self.account.site_name
        if not is_blank(self.account.partner_id):
            securitySection += "\n<partnerID>%s</partnerID>" % self.account.partner_id
        if not is_blank(self.account.email):
            securitySection += "\n<email>%s</email>" % self.account.email
        return WebEx.REQUEST_SCAFFOLD.lstrip() % (securitySection, '%s')
        
    def query(self, body_content, empty_list_ok=False):
        return Response(Request(self.account, body_content), debug=self.debug, xml_override=getattr(self,'xml_override',None), empty_list_ok=empty_list_ok)


