from lxml import etree
import urllib2
import datetime
import dateutil.parser
import pytz
import pprint
import re
from error import WebExError

from utils import is_blank
from request import WebExRequest
from response import WebExResponse

class WebEx(object):

    REQUEST_SCAFFOLD = """
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<serv:message xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">
  <header>
    <securityContext>%s
    </securityContext>
  </header>
  <body>%s
  </body>
</serv:message>
"""

    def __init__(self, webex_id, password, site_id=None, site_name=None, partner_id=None, email=None, debug=False):
        """
        site_id or site_name are required, if both specified, then site_name is used
        if webex_id and email both specified, then email is used -- not sure what that means?
        """
        self.webex_id = webex_id
        self.password = password
        self.site_id = site_id
        self.site_name = site_name
        self.partner_id = partner_id
        self.email = email
        self.debug = debug
  
        self.request_xml = self.build_request_xml()

    def get_api_version(self):
        xml_in = "\n<bodyContent xsi:type=\"java:com.webex.service.binding.ep.GetAPIVersion\"></bodyContent>"
        xml_out = self.query(xml_in).body_content
        version = xml_out.find("{%s}apiVersion"%EP_NS).text
        release = xml_out.find("{%s}release"%EP_NS).text
        return "%s : %s" % (version, release)

        
    def build_request_xml(self):
        if self.site_name and not re.compile(r'^[-a-zA-Z0-9_]*$').match(self.site_name):
            raise WebExError, "site_name is invalid!  It is expected to be an alphanumeric string."
        if is_blank(self.webex_id):
            raise WebExError, "Expected a webexId for API request validations, but did not receive one!"
        if is_blank(self.password):
            raise WebExError, "Expected a password for API request validations, but did not receive one!"
        if is_blank(self.site_id) and is_blank(self.site_name):
            raise WebExError, "Expected a siteId or a siteName for API request validations, but did not receive one!"
        securitySection = "\n<webExID>%s</webExID>" % self.webex_id
        securitySection += "\n<password>%s</password>" % self.password
        if is_blank(self.site_name):
            securitySection += "\n<siteId>%s</siteId>" % self.site_id
        else:
            securitySection += "\n<siteName>%s</siteName>" % self.site_name
        if not is_blank(self.partner_id):
            securitySection += "\n<partnerID>%s</partnerID>" % self.partner_id
        if not is_blank(self.email):
            securitySection += "\n<email>%s</email>" % self.email
        return WebEx.REQUEST_SCAFFOLD.lstrip() % (securitySection, '%s')
        
    def query(self, body_content):
        return WebExResponse(WebExRequest(self, body_content), debug=self.debug)


