import re
from .utils import find, nfind_str, mpop, lazy_property
from . import error
from .exchange import Exchange, BatchListExchange
from .event import GetListedEvents, GetHistoricalEvents


REQUEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<serv:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:serv="http://www.webex.com/schemas/2002/06/service">
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

class Account(object):
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

    @lazy_property
    def version_info(self):
        return GetVersion(self).execute()

    @property
    def version(self):
        return float('.'.join(self.version_info[0].split(' ')[-1].split('V')[-1].split('.')[:2]))

    @property
    def major_version(self):
        return int(self.version)

    @property
    def meetings_require_password(self):
        return find(self.site_instance, 'site:securityOptions', 'site:allMeetingsPassword').text.lower() == 'true'

    @lazy_property
    def site_instance(self):
        return GetSite(self).execute()

    @property
    def listed_events(self):
        return self._listed_batch_list.items

    @property
    def historical_events(self):
        return self._historical_batch_list.items

    @lazy_property
    def events(self):
        #listed_events, historical_events = ParallelBatchList(self._listed_batch_list, self._historical_batch_list).answer
        #listed_events = self.listed_events
        #historical_events
        #ParallelBatchList(self._listed_batch_list).answer
        #listed_events, historical_events = ParallelBatchList(self._listed_batch_list, self._historical_batch_list).answer
        events_hash = dict((e.session_key, e) for e in self.listed_events)
        for e in self.historical_events:
            if events_hash.get(e.session_key):
                events_hash[e.session_key].merge(e)
            else:
                events_hash[e.session_key] = e
        return sorted(events_hash.values(), key=lambda e: e.starts_at)

    @lazy_property
    def _listed_batch_list(self):
        return BatchListExchange(self, GetListedEvents, 'session_key', batch_size=6, overlap=2)

    @lazy_property
    def _historical_batch_list(self):
        return BatchListExchange(self, GetHistoricalEvents, 'session_key', batch_size=6, overlap=2)


class GetVersion(Exchange):
    def _input(self): return '<bodyContent xsi:type="java:com.webex.service.binding.ep.GetAPIVersion"></bodyContent>'
    def _answer(self, body_content): return (nfind_str(body_content, 'ep:apiVersion'), nfind_str(body_content, 'ep:release'))


class GetSite(Exchange):
    def _input(self): return '<bodyContent xsi:type="java:com.webex.service.binding.site.GetSite" />'
    def _answer(self, body_content): return find(body_content, 'site:siteInstance')

