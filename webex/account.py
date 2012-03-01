import re
import requests
from . import utils as u
from .utils import lazy_property
from . import error
from .base import Base
from lxml import etree

#TODO: allow async requests through requests-- would have to break out each api calling property into its own class that could build a request and also produce a response and do a similar thing to what requests does with async.map, just implement a level up inside of here on top of async.map

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

VERSION_XML = '<bodyContent xsi:type=\"java:com.webex.service.binding.ep.GetAPIVersion\"></bodyContent>'
SITE_INSTANCE_XML = '<bodyContent xsi:type="java:com.webex.service.binding.site.GetSite" />'

class Account(Base):
    def __init__(self, **kwargs):
        super(Account, self).__init__()
        self.username = u.nstrip(u.mpop(kwargs, 'webex_id', 'webexId', 'webExID', 'username'))
        self.password = u.nstrip(u.mpop(kwargs, 'password'))
        self.site_name = u.nstrip(u.mpop(kwargs, 'site_name', 'siteName', fallback='').split('.')[0].split('/')[-1]) or None

        if not self.username:
            raise error.InvalidAccount("No webex_id/username specified!")
        if not self.password:
            raise error.InvalidAccount("No password specified!")
        if not self.site_name or not re.compile(r'^[-a-zA-Z0-9_]*$').match(self.site_name):
            raise error.InvalidAccount("'%s' is not a valid site_name" % self.site_name)
        self.api_url = 'https://%s.webex.com/WBXService/XMLService' % self.site_name
        self.request_xml_template = REQUEST_XML % self.__dict__


    def request_etree(self, xml_body, **options):
        options.setdefault('timeout',10)
        try:
            result = requests.post(self.api_url, self.request_xml_template % {'body':xml_body}, **options)
        except requests.exception.Timeout:
            self._reraise(error.TimeoutError(options['timeout']))
        except requests.exception.RequestException:
            self._reraise(error.RequestError())
        if result.status_code != 200:
            raise error.ServerError(result)
        try:
            root = etree.fromstring(result.content)
        except:
            u.reraise(error.ParseError(result.content))

        response = u.traverse(root, 'serv:header', 'serv:response')
        success = u.traverse(response, 'serv:result').text == "SUCCESS"
        gsb_status = u.ntraverse_text(response, 'serv:gsbStatus')
        exception_id = u.nint(u.ntraverse_text(response, 'serv:exceptionID'))
        reason = u.ntraverse_text(response, 'serv:reason')
        value = u.ntraverse_text(response, 'serv:value')
        if exception_id: raise error.ApiError(success, exception_id, reason, value, gsb_status)
        return u.traverse(root, 'serv:body', 'serv:bodyContent')

    @lazy_property
    def version_info(self):
        body = self.request_etree(VERSION_XML)
        return (u.ntraverse_text(body, 'ep:apiVersion'), u.ntraverse_text(body, 'ep:release'))

    @property
    def version(self):
        print self.version_info[0].split(' ')[-1]
        print self.version_info[0].split(' ')[-1].split('V')[-1]
        print self.version_info[0].split(' ')[-1].split('V')[-1].split('.')[:2]
        float('.'.join(self.version_info[0].split(' ')[-1].split('V')[-1].split('.')[:2]))

    @property
    def major_version(self):
        return int(self.version)

    @property
    def meetings_require_password(self):
        return u.traverse(self.site_instance, 'site:securityOptions', 'site:allMeetingsPassword').text.lower() == 'true'

    @property
    def _account(self): return self

    @lazy_property
    def site_instance(self):
        return u.traverse(self.request_etree(SITE_INSTANCE_XML),'site:siteInstance')

    @lazy_property
    def events(self):
        return Event.all()
        return u.traverse()

    @lazy_property
    def normal_events(self):
        return Event.all_l
        return u.traverse()

    def historical_events(self):
        return Event.all_historical()

    def query_events(self):

    def create_event(self, event):
        :b2




