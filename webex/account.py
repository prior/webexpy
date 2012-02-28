import re
from . import utils as u
from . import error


REQUEST_XML = """
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<serv:message xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">
  <header>
    <securityContext>
      <webExID>%(username)s</webExID>
      <password>%(password)s</password>
      <siteName>%(site_name)s</siteName>
    </securityContext>
  </header>
  <body>
%%(body)s
  </body>
</serv:message>
"""

VERSION_XML = """
    <bodyContent xsi:type=\"java:com.webex.service.binding.ep.GetAPIVersion\">
    </bodyContent>
"""


class Account(object):
    def __init__(self, event, **kwargs):
        self.username = u.nstrip(u.mpop(kwargs, 'webex_id', 'webexId', 'webExID', 'username'))
        self.password = u.nstrip(u.mpop(kwargs, 'password'))
        self.site_name = u.nstrip(u.mpop(kwargs, 'site_name', 'siteName').split('.')[0].split('/')[-1])

        if not self.username:
            raise error.InvalidAccount("No webex_id/username specified!" % self.site_name)
        if not self.password:
            raise error.InvalidAccount("No password specified!" % self.site_name)
        if not re.compile(r'^[-a-zA-Z0-9_]*$').match(self.site_name):
            raise error.InvalidAccount("'%s' is not a valid site_name" % self.site_name)
        self._request_xml = None

    @property
    def request_xml(self):
        if self._request_xml == None:
            self._request_xml = REQUEST_XML % self.__dict__
        return self._request_xml

    @property
    def version(self):
        self.request(VERSION_XML)
        

    @property
    def verison_info(self):
        self.

    def get_api_version(self):
        xml_in = "\n<bodyContent xsi:type=\"java:com.webex.service.binding.ep.GetAPIVersion\"></bodyContent>"
        xml_out = self.query(xml_in).body_content
        version = xml_out.find("{%s}apiVersion"%EP_NS).text
        release_elem = xml_out.find("{%s}release"%EP_NS)
        release = release_elem is not None and release_elem.text or ""
        return "%s : %s" % (version, release)

    @property
    def major_version(self):
        if not self._major_version:
            version = self.get_api_version()
            number = float('.'.join(version.split(' : ')[0].split(' ')[-1].split('V')[-1].split('.')[:2]))
            self._major_version = int(number)
        return self._major_version

