import re
from .xutils import find, nfind_str, mpop, lazy_property
from . import error
from .exchange import Exchange, BatchListExchange, ParallelBatchListExchange
from .event import GetListedEvents, GetHistoricalEvents
from . import event
from . import exchange


REQUEST_XML = u"""<?xml version="1.0" encoding="UTF-8"?>
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

    def clone(self):
        return Account(*self.__dict__)

    @lazy_property
    def version_info(self):
        return GetVersion(self).answer

    @property
    def version(self):
        return float('.'.join(self.version_info[0].split(' ')[-1].split('V')[-1].split('.')[:2]))

    @property
    def major_version(self):
        return int(self.version)

    @property
    def meetings_require_password(self):
        return find(self.site_instance, 'site:securityOptions', 'site:allMeetingsPassword').text.lower() == 'true'

    @property
    def meetings_must_be_unlisted(self):
        return find(self.site_instance, 'site:securityOptions', 'site:allMeetingsUnlisted').text.lower() == 'true'

    @lazy_property
    def site_instance(self):
        return GetSite(self).answer

    @property
    def listed_events(self): return self.get_listed_events()

    @property
    def historical_events(self): return self.get_historical_events()

    @lazy_property
    def events(self): return self.get_events()

    def get_listed_events(self, bust=False):
        if bust: del self._listed_batch_list
        return self._listed_batch_list.items

    def get_historical_events(self, bust=False):
        if bust: del self._historical_batch_list
        return self._historical_batch_list.items

    def get_events(self, bust=False):
        if bust: 
            del self.events
            del self._listed_batch_list
            del self._historical_batch_list
        return ParallelBatchListExchange([self._listed_batch_list, self._historical_batch_list]).items

    def create_events(self, events):
        return exchange.batch_action(event.CreateEvent, events)

    def update_events(self, events):
        return exchange.batch_action(event.UpdateEvent, events)

    def delete_events(self, events):
        return exchange.batch_action(event.DeleteEvent, events)

    @lazy_property
    def _listed_batch_list(self):
        return BatchListExchange(GetListedEvents, self, 'session_key', batch_size=50, overlap=2)

    @lazy_property
    def _historical_batch_list(self):
        return BatchListExchange(GetHistoricalEvents, self, 'session_key', batch_size=50, overlap=2)


    def __repr__(self): return str(self)
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        return "https://%s.webex.com [%s]" % (self.site_name, self.username)



class GetVersion(Exchange):
    def _input(self): return '<bodyContent xsi:type="java:com.webex.service.binding.ep.GetAPIVersion"></bodyContent>'
    def _process_xml(self, body_content): return (nfind_str(body_content, 'ep:apiVersion'), nfind_str(body_content, 'ep:release'))


class GetSite(Exchange):
    def _input(self): return '<bodyContent xsi:type="java:com.webex.service.binding.site.GetSite" />'
    def _process_xml(self, body_content): return find(body_content, 'site:siteInstance')

