import uuid
from .xutils import mpop,nstrip,find,find_all,grab,nfind_str,nlower
from .exchange import Exchange, GetListExchange
from sanetime import time
from . import error
from xml.sax.saxutils import escape as xml_escape

class Registrant(object):
    def __init__(self, event, **kwargs):
        super(Registrant, self).__init__()
        self.event = event
        self.email = nlower(nstrip(mpop(kwargs, 'email', 'attendeeEmail')))
        self.attendee_id = nstrip(mpop(kwargs, 'attendee_id', 'id', 'id_'))
        self.first_name = nstrip(mpop(kwargs, 'first_name', 'firstName', 'first'))
        self.last_name = nstrip(mpop(kwargs, 'last_name', 'lastName', 'last'))
        if kwargs.get('name'): self.name = nstrip(kwargs.pop('name'))
        self.viewings = kwargs.pop('viewings', [])
        started_at = mpop(kwargs, 'started_at', 'startTime')
        stopped_at = mpop(kwargs, 'stopped_at', 'endTime')
        if started_at and stopped_at:
            self._add_viewing((time(started_at), time(stopped_at)))
        self.ip_address = nstrip(mpop(kwargs, 'ip_address', 'ipAddress'))

    @property
    def name(self): return ('%s %s' % (self.first_name or '', self.last_name or '')).strip()
    @name.setter
    def name(self, n):
        parts = n.split(' ')
        self.first_name = self.first_name or ' '.join(parts[0:-1]).strip() or None
        self.last_name = self.last_name or parts[-1].strip() or None

    def _add_viewing(self, new_viewing): # assumes viewings are already sorted as they should be
        size = len(self.viewings)
        start_index = 0
        stop_index = size-1
        for i in xrange(size):
            if new_viewing[0] > self.viewings[i][1]:
                start_index = i+1
        for i in xrange(size-1,-1,-1):
            if new_viewing[1] < self.viewings[i][0]:
                stop_index = i-1
        min_ = min(new_viewing[0],start_index<size and self.viewings[start_index][0] or new_viewing[0])
        max_ = max(new_viewing[1],stop_index>=0 and self.viewings[stop_index][1] or new_viewing[1]) 
        self.viewings[start_index:stop_index+1] = [[min_,max_]] 

    @property
    def started_at(self):
        return self.viewings and self.viewings[0][0] or None

    @property
    def stopped_at(self):
        return self.viewings and self.viewings[-1][1] or None

    @property
    def duration_in_minutes(self):
        return self.stopped_at and self.started_at and (self.stopped_at-self.started_at).m or None

    def merge(self, other):
        for a in ('email','first_name','last_name','ip_address','attendee_id'):
            setattr(self, a, getattr(self, a, None) or getattr(other, a, None))
        for v in other.viewings:
            self._add_viewing(v)
        return self

    #TODO: should this be used for a true equals comparator as well?  not sure..  it's definitely not exactly equal, but maybe it is equal enough for what we want to know
    def __cmp__(self, other):
        attrs = ['email','last_name','first_name','started_at','stopped_at','attendee_id','ip_address','event']
        for a in attrs:
            left = getattr(self,a,None)
            right = getattr(other,a,None)
            if left and right:
                result = cmp(left,right)
                if result != 0: return result
            elif right:
                return -1
            elif left:
                return 1
        return 0

    def clone(self):
        return Registrant(self.event).merge(self)

    def create(self): return CreateRegistrants([self]).answer[0]
    def delete(self): return DeleteRegistrant(self).answer

    @property
    def create_xml(self):
        template = u'<attendees><person>%(first)s%(last)s%(email)s</person>%(session_key)s<joinStatus>ACCEPT</joinStatus><emailInvitations>TRUE</emailInvitations></attendees>'
        template_bits = {
                'first': self.first_name and '<firstName>%s</firstName>'%xml_escape(self.first_name) or '',
                'last': self.last_name and '<lastName>%s</lastName>'%xml_escape(self.last_name) or '',
                'email': '<email>%s</email>'%xml_escape(self.email),
                'session_key': '<sessionKey>%s</sessionKey>'%self.event.session_key }
        return template % template_bits

    def __repr__(self): return str(self)
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        viewings = ' , '.join(["%s - %s" % (v[0].to_timezoned_datetime(self.event.timezone).strftime("%d.%m.%y %H:%M:%S"),v[1].to_timezoned_datetime(self.event.timezone).strftime("%d.%m.%y %H:%M:%S")) for v in self.viewings])
        return u"%s %s %s %s %s %s [ %s ] %s" % (self.viewings and 'A' or 'R', self.attendee_id, self.email, self.first_name, self.last_name, self.duration_in_minutes, viewings, self.ip_address)

    @classmethod
    def random(kls, event, count=None):
        registrants = []
        for i in xrange(count or 1):
            guid = ''.join(str(uuid.uuid4()).split('-'))
            registrants.append( Registrant(
                    event, 
                    first_name = u'John %s <>&\xfc\u2603 ' % guid[:8],
                    last_name = u'Smith %s <>&\xfc\u2603 ' % guid[8:16],
                    email = u'%s.%s@%s.com' % (guid[:8].upper(),guid[:8:16],guid[16:])))
        return count is None and registrants[0] or registrants

class RegistrantExchange(Exchange):
    def __init__(self, registrant, request_opts=None, **opts):
        super(RegistrantExchange, self).__init__(registrant.event.account, request_opts, **opts)
        self.registrant = registrant

class RegistrantsExchange(Exchange):
    def __init__(self, registrants, request_opts=None, **opts):
        super(RegistrantsExchange, self).__init__(registrants[0].event.account, request_opts, **opts)
        self.registrants = registrants

class GetRegistrantsExchange(GetListExchange):
    def __init__(self, event, size=None, offset=None, request_opts=None, **opts):
        super(GetRegistrantsExchange, self).__init__(event.account, size, offset, request_opts, **opts)
        self.event = event

    @classmethod
    def uniqify_list(kls,registrants):
        d = {}
        unique_registrants = []
        for r in registrants:
            if r.email in d: 
                d[r.email].merge(r)
            else:
                d[r.email] = r
                unique_registrants.append(r)
        return unique_registrants


class CreateRegistrants(RegistrantsExchange):
    def __init__(self, registrants, request_opts=None, **opts):
        super(CreateRegistrants, self).__init__(registrants, request_opts, **opts)

    def _input(self): 
        return u'<bodyContent xsi:type= "java:com.webex.service.binding.attendee.RegisterMeetingAttendee">%s</bodyContent>' % ''.join([r.create_xml for r in self.registrants])

    def _process_xml(self, body_content):
        elems = find_all(body_content, 'att:register')
        if len(elems) == len(self.registrants):
            for e,r in zip(elems,self.registrants):
                r.attendee_id = nfind_str(e, 'att:attendeeID')
            return self.registrants
        return []  #TODO: not really sure what to do here.  throw an exception probably?


class DeleteRegistrant(RegistrantExchange):
    def _input(self): 
        if self.registrant.email and self.registrant.event.session_key:
            return u'<bodyContent xsi:type= "java:com.webex.service.binding.attendee.DelMeetingAttendee"><attendeeEmail><email>%s</email><sessionKey>%s</sessionKey></attendeeEmail></bodyContent>' % (self.registrant.email, self.registrant.event.session_key)
        else:
            return u'<bodyContent xsi:type= "java:com.webex.service.binding.attendee.DelMeetingAttendee"><attendeeID>%s</attendeeID></bodyContent>' % self.registrant.attendee_id

    def _process_xml(self, body_content):
        return self.registrant


class GetGeneralRegistrants(GetRegistrantsExchange):
    ns = 'att'

    def process_response(self, response=None): # deal with exception thrown on empty lists
        try:
            return super(GetGeneralRegistrants, self).process_response(response)
        except error.ApiError, err:
            if err.exception_id == 60001:  # thrown when event isn't listed (but it may still be known by the history apis-- so I'm swallowing here
                self._lazy_answer = ([],0)
                return self._lazy_answer
            raise

    def _list_input(self): 
        return u'<bodyContent xsi:type="java:com.webex.service.binding.attendee.LstMeetingAttendee"><meetingKey>%s</meetingKey>%%s</bodyContent>' % self.event.session_key

    def _process_list_xml(self, body_content):
        registrants = []
        for elem in find_all(body_content, 'att:attendee'):
            r = Registrant(self.event, **grab(find(elem,'att:person'),'email','name','firstName','lastName',ns='com'))
            r.attendee_id = nfind_str(elem, 'att:attendeeId')
            registrants.append(r)
        return self.__class__.uniqify_list(registrants)

class GetAttendedRegistrants(GetRegistrantsExchange):
    ns = 'history'
    def _list_input(self): 
        return u'<bodyContent xsi:type= "java:com.webex.service.binding.history.LsteventattendeeHistory"><sessionKey>%s</sessionKey>%%s</bodyContent>' % self.event.session_key
    def _process_list_xml(self, body_content):
        return self.__class__.uniqify_list([Registrant(self.event, **grab(elem, 'attendeeEmail','startTime','endTime','duration','ipAddress', ns='history')) for elem in find_all(body_content, 'history:eventAttendeeHistory')])


