from xml.etree import ElementTree as etree
import urllib2
from . import error
from utils import SERVICE_NS
import logging_glue


class Response(object):
    def __init__(self, request, xml_override=None, empty_list_ok=False):
        super(Response,self).__init__()
        self.log = logging_glue.get_log('webex.response')
        self.request = request
        self.empty_list_ok = empty_list_ok
        self.raw_response = self.exception = None
        self.success = False
        if xml_override is not None:
            self.raw_response = xml_override
        else:
            self.log.debug("REQUEST: \n%s\n\n" % self.request.msg)
            try:
                self.raw_response = urllib2.urlopen(self.request.raw_request).read()
            except urllib2.URLError, err:
                raise error.Error("Unable to open url: %s  [%s]" % (self.request.url, str(err)))
        self.parse()

    def parse(self):
        if self.raw_response is not None:
            self.log.debug("RESPONSE: \n%s\n\n" % etree.tostring(etree.fromstring(self.raw_response), pretty_print=True))
            xml = self.raw_response
            self.body_content = None
            if self.parse_response(etree.fromstring(xml).find("{%s}header"%SERVICE_NS).find("{%s}response"%SERVICE_NS)):
                self.body_content = etree.fromstring(xml).find("{%s}body"%SERVICE_NS).find("{%s}bodyContent"%SERVICE_NS)

    def parse_response(self, response_elem):
        self.success = response_elem.find("{%s}result"%SERVICE_NS).text == "SUCCESS"
        self.gsb_status = response_elem.find("{%s}gsbStatus"%SERVICE_NS).text
        exception_id_elem = response_elem.find("{%s}exceptionID"%SERVICE_NS)
        if exception_id_elem is not None:
            self.exception_id = int(exception_id_elem.text)
        reason_elem = response_elem.find("{%s}reason"%SERVICE_NS)
        if reason_elem is not None:
            self.reason = reason_elem.text
        value_elem = response_elem.find("{%s}value"%SERVICE_NS)
        if value_elem is not None:
            self.value = value_elem.text

        if getattr(self, 'exception_id', None) != None:
            if self.empty_list_ok and self.exception_id==15:
                return True # an empty list should not be considered exceptional by default
            elif self.exception_id==60001:
                raise error.UnknownEventError(self.exception_id, self.reason)
            else:
                raise error.Error(self.exception_id, self.reason)
        #TODO: implement more variants!
        return self.success

        
