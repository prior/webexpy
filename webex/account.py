import re
import requests
from requests import async
from .utils import find, nfind, nfind_str, nfind_int, find_all, mpop, mget, lazy_property, reraise
from . import error
from .base import Base
from lxml import etree
from sanetime import sanetime

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
        self.username = mpop(kwargs, 'webex_id', 'webexId', 'webExID', 'username')
        self.password = mpop(kwargs, 'password')
        self.site_name = mpop(kwargs, 'site_name', 'siteName', fallback='').split('.')[0].split('/')[-1].strip() or None

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
#            result = requests.post(self.api_url, self.request_xml_template % {'body':xml_body}, **options)

            rs = []
            for i in xrange(10):
                rs.append(async.post(self.api_url, self.request_xml_template % {'body':xml_body}, **options))
            print(repr(sanetime()))
            results = async.map(rs,size=1)
            print(repr(sanetime()))
            print len(results)
            result = results[-1]
        except requests.exceptions.Timeout:
            self._reraise(error.TimeoutError(options['timeout']))
        except requests.exceptions.RequestException:
            self._reraise(error.RequestError())
        if result.status_code != 200:
            raise error.ServerError(result)
        try:
            root = etree.fromstring(result.content)
        except:
            reraise(error.ParseError(result.content))

        response = find(root, 'serv:header', 'serv:response')
        success = find(response, 'serv:result').text.lower() == "success"
        gsb_status = nfind_str(response, 'serv:gsbStatus')
        exception_id = nfind_int(response, 'serv:exceptionID')
        reason = nfind_str(response, 'serv:reason')
        value = nfind_str(response, 'serv:value')
        if exception_id: raise error.ApiError(success, exception_id, reason, value, gsb_status)
        return find(root, 'serv:body', 'serv:bodyContent')

    @lazy_property
    def version_info(self):
        body = self.request_etree(VERSION_XML)
        return (nfind_str(body, 'ep:apiVersion'), nfind_str(body, 'ep:release'))

    @property
    def version(self):
        float('.'.join(self.version_info[0].split(' ')[-1].split('V')[-1].split('.')[:2]))

    @property
    def major_version(self):
        return int(self.version)

    @property
    def meetings_require_password(self):
        return find(self.site_instance, 'site:securityOptions', 'site:allMeetingsPassword').text.lower() == 'true'

    @property
    def _account(self): return self

    @lazy_property
    def site_instance(self):
        return find(self.request_etree(SITE_INSTANCE_XML),'site:siteInstance')

    #@lazy_property
    #def events(self):
        #return Event.get_all()
        #return u.traverse()

    #@lazy_property
    #def normal_events(self):
        #return Event.all_l
        #return u.traverse()

    #def historical_events(self):
        #return Event.all_historical()

    #def query_events(self):

    #def create_event(self, event):
        #:b2




