from request import Request
from response import Response
from utils import EP_NS

class BaseController(object):

    def __init__(self, account):
        super(BaseController,self).__init__()
        self.account = account

    def get_api_version(self):
        xml_in = "\n<bodyContent xsi:type=\"java:com.webex.service.binding.ep.GetAPIVersion\"></bodyContent>"
        xml_out = self.query(xml_in).body_content
        version = xml_out.find("{%s}apiVersion"%EP_NS).text
        release = xml_out.find("{%s}release"%EP_NS).text
        return "%s : %s" % (version, release)

    def query(self, body_content, empty_list_ok=False):
        return Response(Request(self.account, body_content), xml_override=getattr(self,'xml_override',None), empty_list_ok=empty_list_ok)


