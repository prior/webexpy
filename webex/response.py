from lxml import etree
import urllib2
import pprint
from error import WebExError

from utils import SERVICE_NS


class WebExResponse(object):
    def __init__(self, webex_request, xml_override=None, debug=False):
        self.webex_request = webex_request
        self.debug = debug
        self.raw_response = self.exception = None
        self.success = False
        if xml_override is not None:
            self.raw_response = xml_override
        else:
            if self.debug:
                print("\n=========== REQUEST \n%s\n\n" % self.webex_request.msg)
            try:
                self.raw_response = urllib2.urlopen(self.webex_request.raw_request).read()
            except urllib2.URLError, err:
                raise WebExError, "Unable to open url: %s  [%s]" % (webex_request.url, str(err))
                #print e
                #self.exception = e
        self.parse()

    def parse(self):
        if self.raw_response is not None:
            if self.debug:
                print("\n=========== RESPONSE \n%s\n\n" % etree.tostring(etree.fromstring(self.raw_response), pretty_print=True))
            xml = self.raw_response
            self.body_content = None
            if self.parse_response(etree.fromstring(xml).find("{%s}header"%SERVICE_NS).find("{%s}response"%SERVICE_NS)):
                self.body_content = etree.fromstring(xml).find("{%s}body"%SERVICE_NS).find("{%s}bodyContent"%SERVICE_NS)

    def parse_response(self, response_elem):
        self.success = response_elem.find("{%s}result"%SERVICE_NS).text == "SUCCESS"
        self.gsb_status = response_elem.find("{%s}gsbStatus"%SERVICE_NS).text
        exception_id_elem = response_elem.find("{%s}exceptionID"%SERVICE_NS)
        if exception_id_elem is not None:
            self.exception_id = exception_id_elem.text
        reason_elem = response_elem.find("{%s}reason"%SERVICE_NS)
        if reason_elem is not None:
            self.reason = reason_elem.text
        value_elem = response_elem.find("{%s}value"%SERVICE_NS)
        if value_elem is not None:
            self.value = value_elem.text

        if getattr(self, 'exception_id', None):
            raise WebExError, "Failure Response from Webex: %s [remote exceptionID: %s]" % (getattr(self,'reason','?'), self.exception_id) 
        #TODO: implement subError gathering as well!
        return self.success

        
